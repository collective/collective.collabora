from future import standard_library

standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.testing import COLLECTIVE_COLLABORA_INTEGRATION_TESTING
from collective.collabora.testing import temporary_registry_record
from plone import api
from unittest import mock

import unittest


class TestUtilsUnit(unittest.TestCase):
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
