from contextlib import contextmanager
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.testing import applyProfile
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
    """Provide a test fixture with a test file."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.collabora)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.collabora:default")
        file_data = (TESTDATA_PATH / "testfile.docx").read_bytes()
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        testfile = api.content.create(
            portal,
            type="File",
            id="testfile",
            title="My test file",
        )
        assert IFile.providedBy(testfile)
        testfile.file = NamedBlobFile(data=file_data, filename="testfile.docx")

        # Configure collabora to an unused port, to prevent accidentally running
        # the tests against an active server in development - and then getting
        # breakage on CI where no such service is running.
        api.portal.set_registry_record(
            "collective.collabora.collabora_server_url",
            "http://host.docker.internal:7777",
        )
        setRoles(portal, TEST_USER_ID, roles_before)


COLLECTIVE_COLLABORA_FIXTURE = CollectiveCollaboraLayer()

COLLECTIVE_COLLABORA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLABORA_FIXTURE,),
    name="CollectiveCollaboraLayer:IntegrationTesting",
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
