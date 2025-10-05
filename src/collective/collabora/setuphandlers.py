# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


def uninstall(context):
    pt = api.portal.get_tool("portal_types")
    ptf = pt["File"]
    actions = [action for action in ptf._actions if action.id != "edit-metadata"]
    for action in actions:
        if action.title == "Open":
            action.title = "Edit"
        if "@@collabora-edit" in action.getActionExpression():
            action.setActionExpression("string:${object_url}/edit")
    ptf._actions = tuple(actions)


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.collabora:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["collective.collabora.upgrades"]
