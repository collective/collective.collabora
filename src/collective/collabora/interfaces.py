# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveCollaboraLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IStoredFile(Interface):
    """Support a minimal set of File accessors across AT and DX.

    This provides a subset of DX INamedBlobFile.

    We register adapters against this custom interface, rather than against
    INamedFile itself, to ensure there cannot be any accidental use of this
    adaptation beyond our narrow use case.
    """

    # provide dynamic lookup of field name for easier customization
    file_field_name = Attribute(
        "Attribute name of the storage field. Typically 'file'."
    )

    # the actual storage api
    data = Attribute("file data")
    filename = Attribute("file name")
    contentType = Attribute("content type")

    def getSize():
        """file size"""


class IDummy(Interface):
    """Disables adaptation for components that are not installed"""
