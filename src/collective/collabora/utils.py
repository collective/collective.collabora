from future import standard_library
from future.utils import bytes_to_native_str as n

standard_library.install_aliases()

from logging import getLogger
from plone import api
from urllib.parse import urlparse

logger = getLogger(__name__)


def disallow(*args, **kwargs):
    """Block py27-only call flows in py3"""
    raise RuntimeError("This code path should never be executed")


def collabora_is_cors():
    """CORS mode is not recommended."""
    portal_parts = urlparse(api.portal.get().absolute_url())
    collabora_parts = urlparse(
        api.portal.get_registry_record(
            n(b"collective.collabora.collabora_server_url"), default=None
        )
    )
    if any(
        [
            portal_parts.scheme != collabora_parts.scheme,
            portal_parts.hostname != collabora_parts.hostname,
            portal_parts.port != collabora_parts.port,
        ]
    ):
        logger.warn("Running the Collabora iframe in CORS mode is not recommended.")
        return True
    return False
