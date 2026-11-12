from collective.collabora.interfaces import IStoredFile
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
        self.assertIsInstance(self.stored_file.data, bytes)
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
