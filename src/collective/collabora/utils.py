from logging import getLogger
from plone import api
from urllib.parse import urlparse

logger = getLogger(__name__)


def collabora_is_cors():
    """CORS mode is not recommended."""
    portal_parts = urlparse(api.portal.get().absolute_url())
    collabora_parts = urlparse(
        api.portal.get_registry_record(
            "collective.collabora.collabora_server_url", default=None
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
