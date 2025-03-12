# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from collective.collabora.utils import disallow
from collective.collabora.utils import human_readable_size

import unittest


class TestUtils(unittest.TestCase):
    def test_human_readable_size(self):
        self.assertEqual(human_readable_size(None), "0 KB")
        self.assertEqual(human_readable_size(""), "0 KB")
        self.assertEqual(human_readable_size("foo"), "foo")
        self.assertEqual(human_readable_size(0), "0 KB")
        self.assertEqual(human_readable_size(540), "1 KB")
        self.assertEqual(human_readable_size(600 * 1024), "600.0 KB")
        self.assertEqual(human_readable_size(1635 * 1024), "1.6 MB")
        self.assertEqual(human_readable_size(1655 * 1024), "1.6 MB")
        self.assertEqual(human_readable_size(1765 * 1024 * 1024), "1.7 GB")

    def test_disallow(self):
        with self.assertRaises(RuntimeError):
            disallow()
        with self.assertRaises(RuntimeError):
            disallow("foo")
        with self.assertRaises(RuntimeError):
            disallow(foo="bar")
