# -*- coding: utf-8 -*-
"""UI tests for this package."""
from __future__ import unicode_literals

from builtins import dict
from builtins import open
from future import standard_library


standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.testing import (  # noqa: E501
    AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from collective.collabora.testing import COLLECTIVE_COLLABORA_INTEGRATION_TESTING
from collective.collabora.testing import temporary_registry_record
from collective.collabora.testing import TESTDATA_PATH
from plone import api
from plone.app.testing import logout

import mock  # unittest.mock backport for both py27 and >= py36
import unittest
import urllib.parse


class TestCoolEdit(unittest.TestCase):
    """Test user interface view."""

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        # py27: TypeError: invalid file: PosixPath('/collective.coll...
        with open(str(TESTDATA_PATH / "server_discovery_xml")) as fh:
            self.server_discovery_xml = fh.read()

    @property
    def view(self):
        """return collabora-edit view instance with pristine accessors to avoid test
        leakage via memoizers.

        To test view.error_msg, store and re-access the returned view.
        """
        return api.content.get_view(
            name="collabora-edit", context=self.portal.testfile, request=self.request
        )

    def test_can_edit_member(self):
        self.assertTrue(self.view.can_edit)

    def test_can_edit_anon(self):
        logout()
        self.assertFalse(self.view.can_edit)

    def test_download_url(self):
        self.assertEqual(
            self.view.download_url,
            "http://nohost/plone/testfile/@@download/file/testfile.docx",
        )

    def test_plone_server_url_default(self):
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertEqual(view.plone_server_url, "http://nohost/plone")

    def test_plone_server_url_error(self):
        view = self.view
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://localhost:8080/plone",
        ):
            self.assertEqual(view.plone_server_url, "")
        self.assertEqual(view.error_msg, "error_plone_server_url")

    def test_collabora_server_url_default(self):
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        # This is the fake collabora_server_url in tests, not the actual :default value
        self.assertEqual(view.collabora_server_url, "http://host.docker.internal:7777")

    def test_collabora_server_url_error(self):
        view = self.view
        with temporary_registry_record("collective.collabora.collabora_server_url", ""):
            self.assertEqual(view.collabora_server_url, "")
        self.assertEqual(view.error_msg, "error_collabora_server_url")

    def test_editor_url_error_no_collabora_server_url(self):
        view = self.view
        with temporary_registry_record("collective.collabora.collabora_server_url", ""):
            self.assertIsNone(view.editor_url)
        self.assertEqual(view.error_msg, "error_collabora_server_url")

    def test_editor_url_error_unreachable_collabora_server_url(
        self,
    ):
        view = self.view
        self.assertIsNone(view.editor_url)
        self.assertEqual(view.error_msg, "error_server_discovery")

    @mock.patch("requests.get")
    def test_editor_url_default(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertIsNotNone(view.editor_url)
        self.assertEqual(
            view.editor_url,
            "http://host.docker.internal:9980/browser/55317ef/cool.html?",
        )
        self.assertIsNone(view.error_msg)

    @unittest.skipIf(utils.IS_PLONE4, "Archetypes is too convoluted to support fixture")
    @mock.patch("requests.get")
    def test_editor_url_invalid_mimetype(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        self.portal.testfile.file.contentType = "invalid/mimetype"
        view = self.view
        self.assertIsNone(view.editor_url)
        self.assertEqual(view.error_msg, "error_editor_mimetype")

    @mock.patch("requests.get")
    def test_editor_url_invalid_urlsrc(self, requests_get):
        requests_get.return_value.configure_mock(
            **dict(text=self.server_discovery_xml.replace("urlsrc", "no_urlsrc"))
        )
        view = self.view
        self.assertIsNone(view.editor_url)
        self.assertEqual(view.error_msg, "error_editor_urlsrc")

    def test_jwt_token_default(self):
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertIsNotNone(view.jwt_token)
        self.assertTrue(len(view.jwt_token) > 80)  # 133 actually, but be flexible

    def test_jwt_token_error(self):
        view = self.view
        with mock.patch.object(
            self.portal.acl_users.plugins, "listPlugins", return_value=[]
        ):
            self.assertIsNone(view.jwt_token)
        self.assertEqual(view.error_msg, "error_jwt_plugin")

    @mock.patch("requests.get")
    def test_wopi_url_default(self, requests_get):
        from plone.uuid.interfaces import IUUID

        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertIn("cool.html", view.wopi_url)
        self.assertIn("WOPISrc=", view.wopi_url)
        self.assertIn("testfile", view.wopi_url)
        self.assertIn("%40%40collabora-wopi%2Ffiles", view.wopi_url)
        self.assertIn(IUUID(self.portal.testfile), view.wopi_url)
        self.assertIn("access_token=", view.wopi_url)
        self.assertIn("_authenticator=", view.wopi_url)
        wopi_src = urllib.parse.parse_qs(
            urllib.parse.urlparse(view.wopi_url).query
        ).get("WOPISrc")[0]
        self.assertTrue(wopi_src.startswith("http://nohost/plone/"))

    @mock.patch("requests.get")
    def test_wopi_url_override_plone_server_url(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        with temporary_registry_record(
            "collective.collabora.plone_server_url", "http://some.where:1234/plone"
        ):
            view = self.view
            self.assertIsNone(view.error_msg, view.error_msg)
            self.assertIsNotNone(view.wopi_url)
            self.assertTrue(
                view.wopi_url.startswith("http://host.docker.internal:9980/browser/")
            )
            wopi_src = urllib.parse.parse_qs(
                urllib.parse.urlparse(view.wopi_url).query
            ).get("WOPISrc")[0]
        self.assertTrue(wopi_src.startswith("http://some.where:1234/plone/"))

    def test_iframe_is_cors(self):
        self.assertTrue(self.view.iframe_is_cors)

    @mock.patch("requests.get")
    def test__call__render(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        html = view()
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertIn("Edit metadata", html)
        self.assertIn("<iframe", html)

    #
    # ensure __call__ sets error_msg for use in template
    #

    @mock.patch("requests.get")
    def test__call__plone_server_url_error(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://localhost:8080/plone",
        ):
            view()
        self.assertEqual(view.error_msg, "error_plone_server_url")

    @unittest.skipIf(utils.IS_PLONE4, "Archetypes is too convoluted to support fixture")
    @mock.patch("requests.get")
    def test__call__editor_url_invalid_mimetype(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        self.portal.testfile.file.contentType = "invalid/mimetype"
        view = self.view
        view()
        self.assertEqual(view.error_msg, "error_editor_mimetype")

    @mock.patch("requests.get")
    def test__call__jwt_token_error(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        with mock.patch.object(
            self.portal.acl_users.plugins, "listPlugins", return_value=[]
        ):
            view()
        self.assertEqual(view.error_msg, "error_jwt_plugin")


@unittest.skipUnless(utils.IS_PLONE4, "Archetypes tested only in Plone4")
class ATTestCoolEdit(TestCoolEdit):
    """Test user interface view against Archetypes"""

    layer = AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING
