# -*- coding: utf-8 -*-
"""Init and utils."""
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("collective.collabora")
