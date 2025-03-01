# -*- coding: utf-8 -*-
from contextlib import contextmanager
from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.testing import z2

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
        with open(TESTDATA_PATH / "testfile.docx", "br") as fh:
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


COLLECTIVE_COLLABORA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COLLABORA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveCollaboraLayer:AcceptanceTesting",
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
