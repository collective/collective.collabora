# -*- coding: utf-8 -*-
from BTrees.IFBTree import IFBTree
from BTrees.IIBTree import IIBTree
from BTrees.IOBTree import IOBTree
from BTrees.LFBTree import LFBTree
from BTrees.LLBTree import LLBTree
from BTrees.LOBTree import LOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OLBTree import OLBTree
from BTrees.OOBTree import OOBTree
from zope.globalrequest import getRequest

import logging


SAFE_WRITE_KEY = "plone.protect.safe_oids"

BTREE_TYPES = (
    IFBTree,
    IIBTree,
    IOBTree,
    LFBTree,
    LLBTree,
    LOBTree,
    OIBTree,
    OLBTree,
    OOBTree,
)

LOGGER = logging.getLogger("plone.protect")
_default = []


def safeWrite(obj, request=None):
    if request is None:
        request = getRequest()
    if request is None or getattr(request, "environ", _default) is _default:
        # Request not found or it is a TestRequest without an environment.
        LOGGER.debug("could not mark object as a safe write")
        return
    if SAFE_WRITE_KEY not in request.environ:
        request.environ[SAFE_WRITE_KEY] = []
    try:
        if obj._p_oid not in request.environ[SAFE_WRITE_KEY]:
            request.environ[SAFE_WRITE_KEY].append(obj._p_oid)
        if isinstance(obj, BTREE_TYPES):
            bucket = obj._firstbucket
            while bucket:
                if bucket._p_oid not in request.environ[SAFE_WRITE_KEY]:
                    request.environ[SAFE_WRITE_KEY].append(bucket._p_oid)
                bucket = bucket._next
    except AttributeError:
        LOGGER.debug("object you attempted to mark safe does not have an oid")
