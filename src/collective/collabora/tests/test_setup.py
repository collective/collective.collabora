"""Setup tests for this package."""

from future import standard_library
from future.utils import bytes_to_native_str as n

standard_library.install_aliases()

from collective.collabora.interfaces import IStoredFile
from collective.collabora.testing import (  # noqa: E501
    COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from collective.collabora.testing import TESTDATA_PATH
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.collabora is properly installed."""

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.collabora is installed."""
        self.assertTrue(self.installer.is_product_installed(n(b"collective.collabora")))

    def test_browserlayer(self):
        """Test that ICollectiveCollaboraLayer is registered."""
        from collective.collabora.interfaces import ICollectiveCollaboraLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveCollaboraLayer, utils.registered_layers())

    def test_hidden_profiles(self):
        from plone.base.interfaces import INonInstallable
        from zope.component import getAllUtilitiesRegisteredFor

        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        my_utils = [x for x in utils if n(b"collective.collabora") in repr(x)]
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
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product(n(b"collective.collabora"))
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.collabora is cleanly uninstalled."""
        self.assertFalse(
            self.installer.is_product_installed(n(b"collective.collabora"))
        )

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
        # py27: TypeError: invalid file: PosixPath('/collective.coll...
        with open(str(TESTDATA_PATH / "testfile.docx"), "br") as fh:
            file_data = fh.read()

        self.assertEqual(self.portal.testfile.title, "My test file")
        # use the adapter to get a consistent file API across DX/AT
        stored_file = IStoredFile(self.portal.testfile)
        self.assertEqual(stored_file.data, file_data)
        self.assertEqual(stored_file.filename, "testfile.docx")
