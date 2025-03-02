# -*- coding: utf-8 -*-
"""Callback API tests for this package.


Functional tests verifying authentication with zope.testbrowser are not
included: trying to implement those breaks on a
ZODB.POSException.ConnectionStateError. Let's simply trust the plone.restapi JWT
token authentication, and verify permission checks by directly logging in here.
"""
from collective.collabora.testing import (  # noqa: E501
    COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import logout
from plone.event.utils import pydt
from plone.uuid.interfaces import IUUID

import datetime
import io
import json
import unittest


class TestCoolWOPI(unittest.TestCase):
    """Test user interface view."""

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.uid = IUUID(self.portal.testfile)

    def test_publishTraverse_wopi_mode_file_info(self):
        request = self.request.clone()
        request.set("PATH_INFO", f"/plone/testfile/@@cool_wopi/files/{self.uid}")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        view.publishTraverse(request, self.uid)
        self.assertEqual(view.wopi_mode, "file_info")

    def test_publishTraverse_wopi_mode_contents(self):
        request = self.request.clone()
        request.set(
            "PATH_INFO", f"/plone/testfile/@@cool_wopi/files/{self.uid}/contents"
        )
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        view.publishTraverse(request, "contents")
        self.assertEqual(view.wopi_mode, "contents")

    def test_publishTraverse_invalid_uid_base(self):
        request = self.request.clone()
        uid = "some-invalid-uid"
        request.set("PATH_INFO", f"/plone/testfile/@@cool_wopi/files/{uid}")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        view.publishTraverse(request, uid)
        self.assertIsNone(view.wopi_mode)

    def test_publishTraverse_invalid_uid_contents(self):
        request = self.request.clone()
        uid = "some-invalid-uid"
        request.set("PATH_INFO", f"/plone/testfile/@@cool_wopi/files/{uid}/contents")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        with self.assertRaises(AssertionError):
            view.publishTraverse(request, "contents")
        self.assertIsNone(view.wopi_mode)

    def test_publishTraverse_missing_files_base(self):
        request = self.request.clone()
        request.set("PATH_INFO", f"/plone/testfile/@@cool_wopi/{self.uid}")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        view.publishTraverse(request, self.uid)
        self.assertIsNone(view.wopi_mode)

    def test_publishTraverse_missing_files_contents(self):
        request = self.request.clone()
        request.set("PATH_INFO", f"/plone/testfile/@@cool_wopi/{self.uid}/contents")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        view.publishTraverse(request, "contents")
        self.assertIsNone(view.wopi_mode)

    def test_wopi_check_file_info_member(self):
        view = api.content.get_view("cool_wopi", self.portal.testfile, self.request)
        file_info = json.loads(view.wopi_check_file_info())
        expected = {
            "BaseFileName": "testfile.docx",
            "Size": 6132,
            "OwnerId": "test_user_1_",
            "UserId": "test_user_1_",
            "UserCanWrite": True,
            "UserFriendlyName": "test_user_1_",
            "UserCanNotWriteRelative": True,
            "LastModifiedTime": self.portal.testfile.modified().ISO(),
            "PostMessageOrigin": "http://nohost/plone/testfile",
        }
        self.assertDictEqual(file_info, expected)

    def test_wopi_check_file_info_anon(self):
        logout()
        view = api.content.get_view("cool_wopi", self.portal.testfile, self.request)
        file_info = json.loads(view.wopi_check_file_info())
        expected = {
            "BaseFileName": "testfile.docx",
            "Size": 6132,
            "OwnerId": "test_user_1_",
            "UserId": None,
            "UserCanWrite": False,
            "UserFriendlyName": None,
            "UserCanNotWriteRelative": True,
            "LastModifiedTime": self.portal.testfile.modified().ISO(),
            "PostMessageOrigin": "http://nohost/plone/testfile",
        }
        self.assertDictEqual(file_info, expected)

    def test_wopi_get_file(self):
        view = api.content.get_view("cool_wopi", self.portal.testfile, self.request)
        file_data = view.wopi_get_file()
        self.assertEqual(file_data, self.portal.testfile.file.data)

    def test_wopi_put_file_outdated(self):
        new_data_io = io.BytesIO(b"Really Fake Byte Payload")
        new_data = new_data_io.read()
        new_data_io.seek(0)
        old_data = self.portal.testfile.file.data
        self.assertNotEqual(old_data, new_data)

        request = self.request.clone()
        request._file = new_data_io

        user_version_timestamp = pydt(
            self.portal.testfile.modified()
        ) - datetime.timedelta(minutes=2)
        request.set("HTTP_X_COOL_WOPI_TIMESTAMP", user_version_timestamp.isoformat())
        request.set("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", "true")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        payload = view.wopi_put_file()
        self.assertDictEqual(json.loads(payload), {"COOLStatusCode": 1010})
        self.assertEqual(view.request.response.status, 409)
        self.assertEqual(self.portal.testfile.file.data, old_data)

    def test_wopi_put_file_write_member(self):
        new_data_io = io.BytesIO(b"Really Fake Byte Payload")
        new_data = new_data_io.read()
        new_data_io.seek(0)
        self.assertNotEqual(self.portal.testfile.file.data, new_data)

        request = self.request.clone()
        request._file = new_data_io

        request.set("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", "true")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        payload = view.wopi_put_file()
        self.assertDictEqual(json.loads(payload), {})
        self.assertEqual(view.request.response.status, 200)
        self.assertEqual(self.portal.testfile.file.data, new_data)

    def test_wopi_put_file_write_anon(self):
        new_data_io = io.BytesIO(b"Really Fake Byte Payload")
        new_data = new_data_io.read()
        new_data_io.seek(0)
        old_data = self.portal.testfile.file.data
        self.assertNotEqual(self.portal.testfile.file.data, new_data)

        logout()
        request = self.request.clone()
        request._file = new_data_io

        request.set("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", "true")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        payload = view.wopi_put_file()
        self.assertDictEqual(json.loads(payload), {})
        self.assertEqual(view.request.response.status, 403)
        self.assertEqual(self.portal.testfile.file.data, old_data)

    def test_wopi_put_file_fallthrough(self):
        new_data_io = io.BytesIO(b"Really Fake Byte Payload")
        old_data = self.portal.testfile.file.data

        request = self.request.clone()
        request._file = new_data_io

        view = api.content.get_view("cool_wopi", self.portal.testfile, request)
        payload = view.wopi_put_file()
        self.assertDictEqual(json.loads(payload), {})
        self.assertEqual(view.request.response.status, 400)
        self.assertEqual(self.portal.testfile.file.data, old_data)

    def test_wopi_put_file_write_notifies_ObjectModifiedEvent(self):
        from plone.app.contenttypes.interfaces import IFile

        import zope.component
        import zope.lifecycleevent

        new_data_io = io.BytesIO(b"Really Fake Byte Payload")
        new_data = new_data_io.read()
        new_data_io.seek(0)
        self.assertNotEqual(self.portal.testfile.file.data, new_data)

        request = self.request.clone()
        request._file = new_data_io

        request.set("HTTP_X_COOL_WOPI_ISMODIFIEDBYUSER", "true")
        view = api.content.get_view("cool_wopi", self.portal.testfile, request)

        event_handler = unittest.mock.MagicMock()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerHandler(
            event_handler, (IFile, zope.lifecycleevent.IObjectModifiedEvent)
        )
        try:
            payload = view.wopi_put_file()
        finally:
            gsm.unregisterHandler(
                event_handler, (IFile, zope.lifecycleevent.IObjectModifiedEvent)
            )

        event_handler.assert_called_once()
        self.assertEqual(len(event_handler.call_args[0]), 2)
        _object, _event = event_handler.call_args[0]
        self.assertEqual(_object, self.portal.testfile)
        self.assertEqual(_object.file.data, new_data)
        self.assertEqual(_event.object, self.portal.testfile)
        self.assertEqual(_event.object.file.data, new_data)

        self.assertDictEqual(json.loads(payload), {})
        self.assertEqual(view.request.response.status, 200)
