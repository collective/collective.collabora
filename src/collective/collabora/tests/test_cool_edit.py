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
        """return cool_edit view instance with pristine accessors to avoid test
        leakage via memoizers.

        To test view.error_msg, store and re-access the returned view.
        """
        return api.content.get_view(
            name="cool_edit", context=self.portal.testfile, request=self.request
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

    def test_portal_url_default(self):
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        self.assertEqual(view.portal_url, "http://nohost/plone")

    def test_portal_url_error(self):
        view = self.view
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://localhost:8080/plone",
        ):
            self.assertIsNone(view.portal_url)
        self.assertEqual(view.error_msg, "error_portal_url")

    def test_collabora_url_default(self):
        view = self.view
        self.assertIsNone(view.error_msg, view.error_msg)
        # This is the fake collabora_url in tests, not the actual :default value
        self.assertEqual(view.collabora_url, "http://host.docker.internal:7777")

    def test_collabora_url_error(self):
        view = self.view
        with temporary_registry_record("collective.collabora.collabora_url", ""):
            self.assertEqual(view.collabora_url, "")
        self.assertEqual(view.error_msg, "error_collabora_url")

    def test_editor_url_server_discovery_xml_error_no_collabora_url(self):
        view = self.view
        with temporary_registry_record("collective.collabora.collabora_url", ""):
            self.assertIsNone(view.editor_url)
        self.assertEqual(view.error_msg, "error_collabora_url")

    def test_editor_url_server_discovery_xml_error_unreachable_collabora_url(self):
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
        self.assertIsNotNone(view.wopi_url)
        self.assertIn("cool.html", view.wopi_url)
        self.assertIn("WOPISrc=", view.wopi_url)
        self.assertIn("testfile", view.wopi_url)
        self.assertIn("%40%40cool_wopi%2Ffiles", view.wopi_url)
        self.assertIn(IUUID(self.portal.testfile), view.wopi_url)
        self.assertIn("access_token=", view.wopi_url)

    def test_iframe_is_cors_false(self):
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_url", "http://some.host:8080/cool"
            ):
                self.assertFalse(self.view.iframe_is_cors)

    def test_iframe_is_cors_scheme(self):
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_url", "https://some.host:8080/cool"
            ):
                self.assertTrue(self.view.iframe_is_cors)

    def test_iframe_is_cors_host(self):
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_url",
                "https://another.some.host:8080/cool",
            ):
                self.assertTrue(self.view.iframe_is_cors)

    def test_iframe_is_cors_port(self):
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_url", "http://some.host:8090"
            ):
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
    def test__call__portal_url_error(self, requests_get):
        requests_get.return_value.configure_mock(**dict(text=self.server_discovery_xml))
        view = self.view
        with mock.patch.object(
            self.portal,
            "absolute_url",
            return_value="http://localhost:8080/plone",
        ):
            view()
        self.assertEqual(view.error_msg, "error_portal_url")

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
