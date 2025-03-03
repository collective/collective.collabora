# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from builtins import open
from future import standard_library

# plone.api.portal.set_registry_record expects a native string in py27
from future.utils import bytes_to_native_str as n


standard_library.install_aliases()
from contextlib import contextmanager
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile

import collective.collabora
import os
import pathlib


TESTDATA_PATH = pathlib.Path(os.path.dirname(__file__)) / "testdata"


class CollectiveCollaboraLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.collabora)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.collabora:default")
        # py27: TypeError: invalid file: PosixPath('/collective.coll...
        with open(str(TESTDATA_PATH / "testfile.docx"), "br") as fh:
            file_data = fh.read()
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        api.content.create(
            portal,
            type="File",
            id="testfile",
            title="My test file",
            file=NamedBlobFile(data=file_data, filename="testfile.docx"),
        )
        # Configure collabora to an unused port, to prevent accidentally running
        # the tests against an active server in development - and then getting
        # breakage on CI where no such service is running.
        api.portal.set_registry_record(
            n(b"collective.collabora.server_url"), "http://host.docker.internal:7777"
        )
        setRoles(portal, TEST_USER_ID, roles_before)


COLLECTIVE_COLLABORA_FIXTURE = CollectiveCollaboraLayer()


COLLECTIVE_COLLABORA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLABORA_FIXTURE,),
    name="CollectiveCollaboraLayer:IntegrationTesting",
)


COLLECTIVE_COLLABORA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_COLLABORA_FIXTURE,),
    name="CollectiveCollaboraLayer:FunctionalTesting",
)


@contextmanager
def temporary_registry_record(key, value):
    """Temporarily set up a registry record"""
    pr = api.portal.get_tool("portal_registry")
    backup = pr._records[key].value
    pr._records[key].value = value
    try:
        yield value
    finally:
        pr._records[key].value = backup
