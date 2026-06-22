# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.interfaces import IStoredFile
from collective.collabora.testing import (  # noqa: E501
    AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from collective.collabora.testing import COLLECTIVE_COLLABORA_INTEGRATION_TESTING

import unittest


class TestDXStoredFile(unittest.TestCase):

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.stored_file = IStoredFile(self.portal.testfile)

    def test_context(self):
        self.assertEqual(self.stored_file.context, self.portal.testfile)

    def test_filename(self):
        self.assertEqual(self.stored_file.filename, "testfile.docx")

    def test_contentType(self):
        self.assertEqual(
            self.stored_file.contentType,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    def test_data(self):
        # not testing type(data) since this code covers both py2 and py3
        self.assertEqual(len(self.stored_file.data), 6132)

    def test_getSize(self):
        self.assertEqual(self.stored_file.getSize(), 6132)

    def test_set_data(self):
        self.stored_file.data = b"1234"
        self.assertEqual(self.portal.testfile.file.data, b"1234")

    def test_custom_file_field_name(self):
        from collective.collabora.adapters import DXStoredFile
        from plone.namedfile.file import NamedBlobFile

        self.portal.testfile.other = NamedBlobFile(
            data=b"abcd", filename="other.txt", contentType="text/plain"
        )

        class MyDXStoredFile(DXStoredFile):
            file_field_name = "other"

        stored = MyDXStoredFile(self.portal.testfile)
        self.assertEqual(stored.filename, "other.txt")
        self.assertEqual(stored.contentType, "text/plain")
        self.assertEqual(stored.data, b"abcd")
        self.assertEqual(stored.getSize(), 4)

    def test_invalid_file_field_name(self):
        from collective.collabora.adapters import DXStoredFile

        class MyDXStoredFile(DXStoredFile):
            file_field_name = "invalid"

        with self.assertRaises(AttributeError):
            MyDXStoredFile(self.portal.testfile)


@unittest.skipUnless(utils.IS_PLONE4, "Archetypes tested only in Plone4")
class TestATStoredFile(TestDXStoredFile):

    layer = AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def test_set_data(self):
        self.stored_file.data = b"1234"
        self.assertEqual(self.portal.testfile.data, b"1234")

    def test_invalid_file_field_name(self):
        """Carefully mock that outside of tests the file field is set
        as a class variable before __init__ is run"""
        from collective.collabora.adapters import ATStoredFile

        class MyATStoredFile(ATStoredFile):
            file_field_name = "invalid"

        with self.assertRaises(AttributeError):
            MyATStoredFile(self.portal.testfile)
