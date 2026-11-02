"""Init and utils."""

from future import standard_library

standard_library.install_aliases()
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("collective.collabora")
