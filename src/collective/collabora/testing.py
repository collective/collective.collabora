# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from builtins import open
from future import standard_library
from future.utils import bytes_to_native_str as n


standard_library.install_aliases()

from collective.collabora import utils
from contextlib import contextmanager
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting as BaseIntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile

import collective.collabora
import os
import pathlib


try:
    from Products.ATContentTypes.interfaces import IATFile
    from StringIO import StringIO  # py27 only
except ImportError:
    from collective.collabora.interfaces import IDummy as IATFile

    StringIO = utils.disallow

TESTDATA_PATH = pathlib.Path(os.path.dirname(__file__)) / "testdata"


class CollectiveCollaboraLayer(PloneSandboxLayer):
    """Provide a test fixture with a test file.

    This is made to work across Plone 6, 5 and 4.

    In Plone4, by default it enables Dexterity; optionally you can get an
    Archetypes based fixture by not enabling Dexterity.
    """

    IS_DX = True

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.collabora)

        # In Plone >= 5, dexterity ships in the default setup.
        # In Plone 4 out of the box, dexterity is not enabled.
        if utils.IS_PLONE4 and self.IS_DX:
            from plone.testing import z2
            from zope.configuration import xmlconfig

            import plone.app.contenttypes

            z2.installProduct(app, "Products.DateRecurringIndex")
            xmlconfig.file(
                "configure.zcml", plone.app.contenttypes, context=configurationContext
            )

    def setUpPloneSite(self, portal):
        if utils.IS_PLONE4 and self.IS_DX:
            applyProfile(portal, "plone.app.contenttypes:default")

        applyProfile(portal, "collective.collabora:default")
        # py27: TypeError: invalid file: PosixPath('/collective.coll...
        with open(str(TESTDATA_PATH / "testfile.docx"), "br") as fh:
            file_data = fh.read()
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        testfile = api.content.create(
            portal,
            type="File",
            id="testfile",
            title="My test file",
        )
        if IATFile.providedBy(testfile):
            # This follows the README.txt in
            # https://github.com/plone/plone.app.blob/tree/master/src/plone/app/blob
            data_wrapper = StringIO(file_data)
            data_wrapper.filename = "testfile.docx"
            testfile.setFile(data_wrapper)
        else:
            assert IFile.providedBy(testfile)
            testfile.file = NamedBlobFile(data=file_data, filename="testfile.docx")

        # Configure collabora to an unused port, to prevent accidentally running
        # the tests against an active server in development - and then getting
        # breakage on CI where no such service is running.
        api.portal.set_registry_record(
            n(b"collective.collabora.server_url"), "http://host.docker.internal:7777"
        )
        setRoles(portal, TEST_USER_ID, roles_before)


class IntegrationTesting(BaseIntegrationTesting):
    """Provide an integration test case aware of AT vs DX"""

    @property
    def IS_DX(self):
        return self.__bases__[0].IS_DX


COLLECTIVE_COLLABORA_FIXTURE = CollectiveCollaboraLayer()

COLLECTIVE_COLLABORA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLABORA_FIXTURE,),
    name="CollectiveCollaboraLayer:IntegrationTesting",
)

# We run Archetypes tests in addition to Dexterity tests,
# but only in Plone4.


class ATCollectiveCollaboraLayer(CollectiveCollaboraLayer):
    IS_DX = False


AT_COLLECTIVE_COLLABORA_FIXTURE = ATCollectiveCollaboraLayer()


AT_COLLECTIVE_COLLABORA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AT_COLLECTIVE_COLLABORA_FIXTURE,),
    name="ATCollectiveCollaboraLayer:IntegrationTesting",
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
