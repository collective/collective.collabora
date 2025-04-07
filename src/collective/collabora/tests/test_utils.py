# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.testing import COLLECTIVE_COLLABORA_INTEGRATION_TESTING
from collective.collabora.testing import temporary_registry_record
from plone import api

import mock  # unittest.mock backport for both py27 and >= py36
import unittest


class TestUtilsUnit(unittest.TestCase):
    def test_human_readable_size(self):
        self.assertEqual(utils.human_readable_size(None), "0 KB")
        self.assertEqual(utils.human_readable_size(""), "0 KB")
        self.assertEqual(utils.human_readable_size("foo"), "foo")
        self.assertEqual(utils.human_readable_size(0), "0 KB")
        self.assertEqual(utils.human_readable_size(540), "1 KB")
        self.assertEqual(utils.human_readable_size(600 * 1024), "600.0 KB")
        self.assertEqual(utils.human_readable_size(1635 * 1024), "1.6 MB")
        self.assertEqual(utils.human_readable_size(1655 * 1024), "1.6 MB")
        self.assertEqual(utils.human_readable_size(1765 * 1024 * 1024), "1.7 GB")

    def test_disallow(self):
        with self.assertRaises(RuntimeError):
            utils.disallow()
        with self.assertRaises(RuntimeError):
            utils.disallow("foo")
        with self.assertRaises(RuntimeError):
            utils.disallow(foo="bar")


class TestUtilsIntegration(unittest.TestCase):
    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def test_collabora_is_cors_default(self):
        self.assertTrue(utils.collabora_is_cors())

    def test_collabora_is_cors_false(self):
        with mock.patch.object(
            api.portal.get(),
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_server_url",
                "http://some.host:8080/cool",
            ):
                self.assertFalse(utils.collabora_is_cors())

    def test_collabora_is_cors_scheme(self):
        with mock.patch.object(
            api.portal.get(),
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_server_url",
                "https://some.host:8080/cool",
            ):
                self.assertTrue(utils.collabora_is_cors())

    def test_collabora_is_cors_host(self):
        with mock.patch.object(
            api.portal.get(),
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_server_url",
                "https://another.some.host:8080/cool",
            ):
                self.assertTrue(utils.collabora_is_cors())

    def test_collabora_is_cors_port(self):
        with mock.patch.object(
            api.portal.get(),
            "absolute_url",
            return_value="http://some.host:8080/plone",
        ):
            with temporary_registry_record(
                "collective.collabora.collabora_server_url", "http://some.host:8090"
            ):
                self.assertTrue(utils.collabora_is_cors())
