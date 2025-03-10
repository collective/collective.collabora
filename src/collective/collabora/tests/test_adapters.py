# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from __future__ import unicode_literals

from builtins import open
from future import standard_library


standard_library.install_aliases()

from collective.collabora.interfaces import IStoredFile
from collective.collabora.testing import (  # noqa: E501
    COLLECTIVE_COLLABORA_INTEGRATION_TESTING,
)
from collective.collabora.testing import TESTDATA_PATH
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestDXStoredFile(unittest.TestCase):
    pass


class TestATStoredFile(unittest.TestCase):
    pass
