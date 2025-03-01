from datetime import datetime
from logging import getLogger
from plone import api
from plone.event.utils import pydt
from plone.memoize.view import memoize
from plone.namedfile.file import NamedBlobFile
from plone.protect.utils import safeWrite
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json


logger = getLogger(__name__)


@implementer(IPublishTraverse)
class CoolWOPIView(BrowserView):
    """Callback view used by Collabora Online to talk to Plone"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.wopi_mode = None

    def publishTraverse(self, request, name, *args, **kwargs):
        """Provide the WOPI endpoints:

        - @@cool_wopi/files/<uid>
        - @@cool_wopi/files/<uid>/contents
        """
        parts = request.get("PATH_INFO").split("/")
        # This is traversed for each part of the URL. Make sure to catch only
        # the "last" traversal, by checking the position of "@@cool_wopi".
        if parts[-3] == "@@cool_wopi" and name == IUUID(self.context):
            assert parts[-2] == "files"
            self.wopi_mode = "file_info"
        elif parts[-4] == "@@cool_wopi" and name == "contents":
            assert parts[-3] == "files"
            assert parts[-2] == IUUID(self.context)
            self.wopi_mode = "contents"
        logger.debug(
            "publishTraverse(): %r, %r, %r (path=%r): wopi_mode = %r",
            name,
            args,
            kwargs,
            request.get("PATH_INFO"),
            self.wopi_mode,
        )
        return self

    def __call__(self):
        logger.debug(
            "%r: %r %r: wopi_mode = %r",
            self.__class__.__name__,
            self.request.method,
            self.request.get("PATH_INFO"),
            self.wopi_mode,
        )
        if self.wopi_mode == "file_info":
            return self.wopi_check_file_info()
        assert self.wopi_mode == "contents"
        if self.request.method == "GET":
            return self.wopi_get_file()
        if self.request.method == "POST":
            return self.wopi_put_file()

    @property
    @memoize
    def can_edit(self):
        return api.user.has_permission(
            "Modify portal content", user=api.user.get_current(), obj=self.context
        )

    def wopi_check_file_info(self):
        """WOPI CheckFileInfo endpoint. Return the file information."""
        logger.debug("wopi_check_file_info: %r", self.context.absolute_url())
        # TODO: CORS header actually not needed.
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")
        self.request.response.setHeader("Content-Type", "application/json")

        file = self.context.file
        user = api.user.get_current()
        user_id = user.getId()
        file_info = {
            "BaseFileName": file.filename,
            "Size": file.getSize(),
            "OwnerId": self.context.getOwner().getId(),
            "UserId": user_id,
            "UserCanWrite": self.can_edit,
            "UserFriendlyName": user.getProperty("fullname") or user_id,
            "UserCanNotWriteRelative": True,  # No "Save As" button
            "LastModifiedTime": self.context.modified().ISO8601(),
            "PostMessageOrigin": self.context.absolute_url(),
        }
        logger.debug(
            "file_info: %r %r %r: %r",
            user_id,
            self.can_edit and "can edit" or "can not edit",
            self.context.absolute_url(),
            file_info,
        )
        return json.dumps(file_info)

    def wopi_get_file(self):
        """WOPI GetFile endpoint. Return the file content."""
        logger.debug("wopi_get_file: %r", self.context.absolute_url())
        # TODO: CORS header actually not needed.
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")

        return self.context.file.data

    def wopi_put_file(self):
        """WOPI PutFile endpoint. Update the file content.

        In addition to the base permission zope2.View, that applies to the
        browser view as a whole, this method performs a write and requires the
        ModifyPortalContent permission on the context object. We use a homegrown
        check for that, since ClassSecurityInfo declarations are suitable to
        protect content object methods, not for browser view methods.
        """
        logger.debug("wopi_put_file: %r", self.context.absolute_url())
        self.request.response.setHeader("Content-Type", "application/json")

        if not self.can_edit:
            self.request.response.setStatus(403)
            # This is not a COOL status message. Just catching that edge case
            return json.dumps(
                {"Status": 403, "Message": "User is not authorized to edit"}
            )

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
            if pydt(self.context.modified()) > user_dt:
                logger.debug(
                    "User changes are outdated. User: <%r>. URL: <%r>.",
                    api.user.get_current().getId(),
                    self.context.absolute_url(),
                )

                self.request.response.setStatus(409)
                return json.dumps({"COOLStatusCode": 1010})

        if self.request.get("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", False):
            # Save changes back, if document was modified.
            #
            # While this is a POST, the request comes from COOL and lacks an
            # authenticator token. Instead of passing that around, using
            # safeWrite is the more convenient way of satisfying plone.protect,
            # and more targeted than IDisableCSRFProtection.
            safeWrite(self.context)

            file = self.context.file
            filename = file.filename
            content_type = file.contentType
            data = self.request._file.read()
            self.context.file = NamedBlobFile(
                data=data, filename=filename, contentType=content_type
            )

            logger.debug(
                "File updated. User: <%r>. URL: <%r>.",
                api.user.get_current().getId(),
                self.context.absolute_url(),
            )

        self.request.response.setStatus(200)
        return json.dumps({})
