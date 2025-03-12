# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from importlib import import_module


IS_PLONE6 = getattr(import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False)
IS_PLONE5 = not IS_PLONE6 and getattr(
    import_module("Products.CMFPlone.factory"), "PLONE52MARKER", False
)
IS_PLONE4 = not (IS_PLONE6 or IS_PLONE5)
PLONE_VERSION = 6 if IS_PLONE6 else 5 if IS_PLONE5 else 4

SIZE_CONST = {
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
    "PB": 1024**5,
}


def human_readable_size(size):
    """plone.base is not available in older Plone versions.
    Reimplement this utility method.
    """
    try:
        size = int(size)
    except (ValueError, TypeError):
        pass
    if not size:
        return "0 KB"
    if not isinstance(size, int):
        return size
    if size < 1024:
        return "1 KB"
    for c in ("PB", "TB", "GB", "MB", "KB"):
        if size // SIZE_CONST[c] > 0:
            break
    fraction = float(size) / SIZE_CONST[c]
    return "%.1f %s" % (fraction, c)


def disallow(*args, **kwargs):
    """Block py27-only call flows in py3"""
    raise RuntimeError("This code path should never be executed")
