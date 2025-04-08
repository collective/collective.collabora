# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from builtins import dict
from builtins import filter
from builtins import next
from builtins import super
from future import standard_library
from future.utils import bytes_to_native_str as n


standard_library.install_aliases()

from collective.collabora import _
from collective.collabora import utils
from collective.collabora.adapters import IStoredFile
from logging import getLogger
from lxml import etree
from plone import api
from plone.app.contenttypes.browser.file import FileView
from plone.memoize.view import memoize
from plone.protect.authenticator import createToken
from plone.uuid.interfaces import IUUID
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from urllib.parse import urlencode
from urllib.parse import urlparse

import requests


logger = getLogger(__name__)

error_server_discovery_msg = _(
    "error_server_discovery", default="Collabora server is not responding."
)


class CollaboraEditView(FileView):
    """User interface for interacting with Collabora Online."""

    def __init__(self, context, request):
        # newsuper throws an infinite loop in py27
        super(FileView, self).__init__(context, request)
        self.error_msg = None
        self.stored_file = IStoredFile(context)

    def __call__(self):
        if not all([self.plone_server_url, self.collabora_server_url, self.wopi_url]):
            # accessing those detects errors and sets self.error_msg
            pass
        return super(FileView, self).__call__()

    def human_readable_size(self):
        """Use our own reimplementation, against our own adapter"""
        return utils.human_readable_size(self.stored_file.getSize())

    @property
    @memoize
    def plone_version(self):
        """Get the major version we're running in."""
        return "plone%i" % utils.PLONE_VERSION

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
                self.stored_file.filename,
            )
        )

    @property
    @memoize
    def portal_url(self):
        """The 'normal' Plone portal url, as used in the"""
        return api.portal.get().absolute_url()

    @property
    @memoize
    def plone_server_url(self):
        """The base URL for Collabora to reach Plone on"""
        plone_server_url = api.portal.get_registry_record(
            n(b"collective.collabora.plone_server_url"), default=None
        )
        if not plone_server_url:
            plone_server_url = self.portal_url
        parts = urlparse(plone_server_url)
        # This assumes you are running Collabora in a docker container,
        # which means it will hit itself and not Plone when trying to contact localhost.
        if parts.hostname in ("localhost", "127.0.0.1"):
            self.error_msg = _(
                "error_plone_server_url",
                default=(
                    "When Plone is supposed to be accessed on localhost, "
                    "Collabora cannot call back. "
                    "Use host.docker.internal or a public FQDN instead."
                ),
            )
            logger.error("When Plone runs on localhost, Collabora cannot call back.")
            return ""
        return plone_server_url

    @property
    @memoize
    def collabora_server_url(self):
        collabora_server_url = api.portal.get_registry_record(
            n(b"collective.collabora.collabora_server_url"), default=None
        )
        if not collabora_server_url:
            self.error_msg = _(
                "error_collabora_server_url_empty",
                default="collective.collabora.collabora_server_url is not configured.",
            )
            logger.error("collective.collabora.collabora_server_url is not configured.")
        if collabora_server_url and not collabora_server_url.startswith("http"):
            self.error_msg = _(
                "error_collabora_server_url_invalid",
                default=(
                    "collective.collabora.collabora_server_url "
                    "needs to be a full URL."
                ),
            )
            logger.error(
                "collective.collabora.collabora_server_url %s needs to be a full URL",
                collabora_server_url,
            )
            return ""  # Don't let server discovery error msg obscure this one
        return collabora_server_url

    @property
    @memoize
    def server_discovery_xml(self):
        if not self.collabora_server_url:
            return
        try:
            response = requests.get("%s/hosting/discovery" % self.collabora_server_url)
        except requests.exceptions.RequestException as e:
            self.error_msg = error_server_discovery_msg
            logger.error(e)
            return
        if response.status_code == 200:
            return response.text
        self.error_msg = error_server_discovery_msg
        logger.error(
            "Server discovery error %i: %s. Verify your proxy configuration.",
            response.status_code,
            response.reason,
        )

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
        mime_type = self.stored_file.contentType
        action = tree.xpath("//app[@name='%s']/action" % mime_type)
        action = action[0] if len(action) else None
        if action is None:
            self.error_msg = _(
                "error_editor_mimetype",
                default="Collabora does not support mimetype ${mimetype}.",
                mapping={"mimetype": mime_type},
            )
            logger.error("Collabora does not support mimetype %r.", mime_type)
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
                default=(
                    "JWT Authentication Plugin not found. "
                    "Is plone.restapi installed?"
                ),
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

        # optionally enable direct backend-to-backend connection
        if self.plone_server_url != self.portal_url:
            document_url = document_url.replace(self.portal_url, self.plone_server_url)

        uuid = IUUID(self.context)
        args = dict(
            WOPISrc="%s/@@collabora-wopi/files/%s" % (document_url, uuid),
            access_token=self.jwt_token,  # login credentials
            _authenticator=createToken(),  # plone.protect
            # https://sdk.collaboraonline.com/docs/theming.html
            ui_defaults=api.portal.get_registry_record(
                n(b"collective.collabora.ui_defaults"),
                default="UIMode=compact;TextSidebar=false;TextRuler=false;PresentationStatusbar=false;SpreadsheetSidebar=false;",  # noqa: E501
            ),
        )
        quoted_args = urlencode(args)
        return "%s%s" % (self.editor_url, quoted_args)

    @property
    @memoize
    def iframe_is_cors(self):
        """
        Requesting fullscreen works only when CORS protection is not in play,
        i.e. when running Collabora Online via a reverse proxy on the same
        domain and port as Plone itself - that is the recommended way of running
        in production.
        """
        return utils.collabora_is_cors()

    @property
    def css_import(self):
        return (
            "@import url(%s/++resource++collective.collabora/edit.css" % self.portal_url
        )
