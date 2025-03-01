from collective.collabora import _
from logging import getLogger
from lxml import etree
from plone import api
from plone.app.contenttypes.browser.file import FileView
from plone.memoize.view import memoize
from plone.uuid.interfaces import IUUID
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin

import requests
import urllib.parse


logger = getLogger(__name__)


class CoolEditView(FileView):
    """User interface for interacting with Collabora Online."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.error_msg = None

    def __call__(self):
        if not all([self.portal_url, self.server_url, self.wopi_url]):
            # accessing those detects errors and sets self.error_msg
            pass
        return super().__call__()

    @property
    @memoize
    def can_edit(self):
        return api.user.has_permission(
            "Modify portal content", user=api.user.get_current(), obj=self.context
        )

    @property
    @memoize
    def download_url(self):
        return "/".join(
            (
                self.context.absolute_url(),
                "@@download",
                "file",
                self.context.file.filename,
            )
        )

    @property
    @memoize
    def portal_url(self):
        portal_url = api.portal.get().absolute_url()
        parts = urllib.parse.urlparse(portal_url)
        if parts.hostname in ("localhost", "127.0.0.1"):
            self.error_msg = _(
                "error_portal_url",
                default=(
                    "When Plone runs on localhost, Collabora cannot call back. "
                    "Use host.docker.internal or a public FQDN instead."
                ),
            )
            logger.error("When Plone runs on localhost, Collabora cannot call back.")
            return
        return portal_url

    @property
    @memoize
    def server_url(self):
        server_url = api.portal.get_registry_record(
            "collective.collabora.server_url", default=None
        )
        if not server_url:
            self.error_msg = _(
                "error_server_url",
                default="collective.collabora.server_url is not configured.",
            )
            logger.error("collective.collabora.server_url is not configured.")
        return server_url

    @property
    @memoize
    def server_discovery_xml(self):
        if not self.server_url:
            return
        try:
            return requests.get(f"{self.server_url}/hosting/discovery").text
        except requests.exceptions.RequestException as e:
            self.error_msg = _(
                "error_server_discovery", default="Collabora server is not responding."
            )
            logger.error(e)
            return

    @property
    @memoize
    def editor_url(self):
        """Return the URL of the LibreOffice / Collabora editor.

        - Call wopi_discovery.
        - Get the right URL depending on the file extension from the XML
        """
        if not self.server_discovery_xml:
            return
        parser = etree.XMLParser()
        tree = etree.fromstring(self.server_discovery_xml, parser=parser)
        # ext = self.context.file.filename.split(".")[-1]
        # action = tree.xpath("//action[@ext='odt']")
        mime_type = self.context.file.contentType
        action = tree.xpath(f"//app[@name='{mime_type}']/action")
        action = action[0] if len(action) else None
        if action is None:
            self.error_msg = _(
                "error_editor_mimetype",
                default="Collabora does not support mimetype ${mimetype}.",
                mapping={"mimetype": mime_type},
            )
            logger.error("Collabora does not support mimetype %s.", mime_type)
            return
        urlsrc = action.get("urlsrc")
        if not urlsrc:
            self.error_msg = _(
                "error_editor_urlsrc", default="Cannot extract url source from action"
            )
            logger.error("Cannot extract urlsrc from action %r", action)
        return urlsrc

    @property
    @memoize
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
        try:
            jwt_plugin = next(plugins)[1]
        except StopIteration:
            self.error_msg = _(
                "error_jwt_plugin",
                default="JWT Authentication Plugin not found. Is plone.restapi installed?",
            )
            logger.error("JWT Authentication Plugin not found.")
            return
        return jwt_plugin.create_token(api.user.get_current().getId())

    @property
    @memoize
    def wopi_url(self):
        """Return the URL to load the document in LibreOffice / Collabora."""
        if not self.editor_url or not self.jwt_token:
            return
        document_url = self.context.absolute_url()
        uuid = IUUID(self.context)
        args = dict(
            WOPISrc=f"{document_url}/@@cool_wopi/files/{uuid}",
            access_token=self.jwt_token,
        )
        quoted_args = urllib.parse.urlencode(args)
        return f"{self.editor_url}{quoted_args}"
