# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.collabora.testing import (  # noqa: E501
    COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from collective.collabora.testing import TESTDATA_PATH
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.collabora is properly installed."""

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.collabora is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.collabora"))

    def test_browserlayer(self):
        """Test that ICollectiveCollaboraLayer is registered."""
        from collective.collabora.interfaces import ICollectiveCollaboraLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveCollaboraLayer, utils.registered_layers())

    def test_hidden_profiles(self):
        from plone.base.interfaces import INonInstallable
        from zope.component import getAllUtilitiesRegisteredFor

        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        my_utils = [x for x in utils if "collective.collabora" in repr(x)]
        self.assertEqual(len(my_utils), 1)
        my_hidden = my_utils[0]
        self.assertEqual(
            my_hidden.getNonInstallableProducts(), ["collective.collabora.upgrades"]
        )
        self.assertEqual(
            my_hidden.getNonInstallableProfiles(), ["collective.collabora:uninstall"]
        )


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.collabora")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.collabora is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("collective.collabora"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveCollaboraLayer is removed."""
        from collective.collabora.interfaces import ICollectiveCollaboraLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveCollaboraLayer, utils.registered_layers())


class TestFixture(unittest.TestCase):

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_testfile_created(self):
        with open(TESTDATA_PATH / "testfile.docx", "br") as fh:
            file_data = fh.read()

        self.assertEqual(self.portal.testfile.title, "My test file")
        self.assertEqual(self.portal.testfile.file.data, file_data)
        self.assertEqual(self.portal.testfile.file.filename, "testfile.docx")
