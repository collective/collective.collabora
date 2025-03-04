# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveCollaboraLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
