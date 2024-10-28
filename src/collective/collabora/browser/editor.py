from datetime import datetime
from logging import getLogger
from lxml import etree
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.protect.interfaces import IDisableCSRFProtection
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json
import requests


logger = getLogger(__name__)


@implementer(IPublishTraverse)
class EditorView(BrowserView):
    """LibreOffice / Collabora editor view."""

    wopi_mode = None

    def publishTraverse(self, request, name, *args, **kwargs):
        """Provide the WOPI endpoints:

            - @editor/wopi/files/<id>
            - @editor/wopi/files/<id>/contents

        or fall back to the default view.
        """
        parts = request.environ["REQUEST_URI"].split("/")

        if parts[-3] == "wopi" and parts[-2] == "files" and name == IUUID(self.context):
            self.wopi_mode = "file_info"
        elif (
            parts[-4] == "wopi"
            and parts[-3] == "files"
            and parts[-2] == IUUID(self.context)
            and name == "contents"
        ):
            self.wopi_mode = "contents"
        return self

    def __call__(self):
        if self.wopi_mode == "file_info":
            return self.wopi_check_file_info()
        if self.wopi_mode == "contents":
            if self.request.method == "GET":
                return self.wopi_get_file()
            elif self.request.method == "POST":
                return self.wopi_put_file()

        return super().__call__()

    def wopi_get_file(self):
        """WOPI GetFile endpoint.

        Return the file content.
        """

        # TODO: CORS header actually not needed.
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")

        return self.context.file.data

    def wopi_check_file_info(self):
        """WOPI CheckFileInfo endpoint.

        Return the file information.
        """
        # TODO: CORS header actually not needed.
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")
        self.request.response.setHeader("Content-Type", "application/json")

        # NOTE / TODO:
        # There is a difference between different dates of the document:
        # (Pdb++) self.context.modified()
        # DateTime('2021/07/23 00:59:23.820897 GMT+2')
        # (Pdb++) self.context.modified().ISO8601()
        # '2021-07-23T00:59:23+02:00'
        # (Pdb++) self.context.ModificationDate()
        # '2021-07-22T23:59:23+01:00'

        file = self.context.file
        user = api.user.get_current()
        can_edit = api.user.has_permission(
            "Modify portal content", user=user, obj=self.context
        )

        return json.dumps(
            {
                "BaseFileName": file.filename,
                "Size": file.getSize(),
                "OwnerId": self.context.getOwner().getId(),
                "UserId": user.getId(),
                "UserCanWrite": can_edit,
                "UserFriendlyName": user.getProperty("fullname"),
                "UserCanNotWriteRelative": True,  # No "Save As" button
                "LastModifiedTime": self.context.modified().ISO8601(),
            }
        )

    def wopi_put_file(self):
        """WOPI PutFile endpoint.

        Update the file content.
        """
        self.request.response.setHeader("Content-Type", "application/json")

        # TODO:
        # - Check locking (see ploneintranet.workspace.basecontent.baseviews.BaseView)
        # - Check autosave (see same)
        # - Should we derive from BaseView and also use reset_dx_modified?
        # - Use ploneintranet.workspace.basecontent.utils.dexterity_update?

        # https://sdk.collaboraonline.com/docs/advanced_integration.html#putfile-headers
        # Relevant headers:
        # - HTTP_X_COOL_WOPI_ISAUTOSAVE
        # - HTTP_X_COOL_WOPI_ISEXITSAVE
        # - HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER
        # - HTTP_X_COOL_WOPI_TIMESTAMP
        user_timestamp = self.request.get("HTTP_X_COOL_WOPI_TIMESTAMP", None)
        if user_timestamp:
            # Document modified by another user. Return and let LibreOffice /
            # Collabora ask the user to overwrite or not. If called again
            # without a HTTP_X_COOL_WOPI_TIMESTAMP, the document is saved
            # regardless of the modification status.
            #
            # See:
            # https://sdk.collaboraonline.com/docs/advanced_integration.html#detecting-external-document-change  # noqa: E501
            #
            user_dt = datetime.fromisoformat(user_timestamp)
            context_timestamp = self.context.modified().ISO8601()
            context_dt = datetime.fromisoformat(context_timestamp)

            if context_dt > user_dt:
                self.request.response.setStatus(409)
                return json.dumps({"COOLStatusCode": 1010})

        if self.request.get("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", False):
            # Save changes back, if document was modified.

            # TODO, maybe do not disable CSRF protection here?
            alsoProvides(self.request, IDisableCSRFProtection)

            file = self.context.file
            filename = file.filename
            content_type = file.contentType
            data = self.request._file.read()
            self.context.file = NamedBlobFile(
                data=data, filename=filename, contentType=content_type
            )

            # TODO: change back to logger.debug when we get a feeling on the
            #       update frequency.
            logger.info(
                f"""File updated.
                    User: {api.user.get_current().getId()},
                    URL: {self.context.absolute_url()}
                """
            )

        # Success.
        self.request.response.setStatus(200)
        return json.dumps({})

    @property
    def wopi_url(self):
        """Return the URL to load the document in LibreOffice / Collabora."""
        editor_url = self.editor_url
        if not editor_url:
            return None
        document_url = self.context.absolute_url()
        uuid = IUUID(self.context)
        return f"{editor_url}?WOPISrc={document_url}/@@editor/wopi/files/{uuid}"

    @property
    def editor_url(self):
        """Return the URL of the LibreOffice / Collabora editor.

        - Call wopi_discovery.
        - Get the right URL depending on the file extension from the XML
        """
        server_url = api.portal.get_registry_record(
            "collective.collabora.server_url", default=None
        )
        if not server_url:
            return None

        # TODO: some error handling in case server is not reachable.
        try:
            xml = requests.get(f"{server_url}/hosting/discovery").text
        except requests.exceptions.RequestException as e:
            logger.error(e)
            raise e
        parser = etree.XMLParser()
        tree = etree.fromstring(xml, parser=parser)
        # ext = self.context.file.filename.split(".")[-1]
        # action = tree.xpath("//action[@ext='odt']")
        mime_type = self.context.file.contentType
        action = tree.xpath(f"//app[@name='{mime_type}']/action")
        action = action[0] if len(action) else None
        if action is None:
            return None
        return action.get("urlsrc")

    @property
    def jwt_token(self):
        """Return a JWT token from the plone.restapi JWT PAS plugin.

        This token is used by the WOPI client (LibreOffice / Collabora)
        to authenticate against the WOPI host (Quaive).
        """
        acl_users = api.portal.get_tool("acl_users")
        plugins = acl_users.plugins.listPlugins(IAuthenticationPlugin)
        plugins = filter(
            lambda it: it[1].meta_type == "JWT Authentication Plugin", plugins
        )
        jwt_plugin = next(plugins)[1]
        return jwt_plugin.create_token(api.user.get_current().getId())
