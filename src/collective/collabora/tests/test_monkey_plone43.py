# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.monkey_plone43.plone_protect_utils import safeWrite
from collective.collabora.testing import AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING
from collective.collabora.testing import COLLECTIVE_COLLABORA_INTEGRATION_TESTING

import unittest


class TestPloneProtectMonkey(unittest.TestCase):
    """Test user interface view."""

    layer = COLLECTIVE_COLLABORA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_safeWrite(self):
        self.assertIsNone(self.request.environ.get("plone.protect.safe_oids"))
        safeWrite(self.portal.testfile)
        # avoid test leakage by popping the changed value off the request
        self.assertEqual(
            self.request.environ.pop("plone.protect.safe_oids"),
            [self.portal.testfile._p_oid],
        )


@unittest.skipUnless(utils.IS_PLONE4, "Archetypes tested only in Plone4")
class TestPloneProtectMonkeyAT(TestPloneProtectMonkey):

    layer = AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING
