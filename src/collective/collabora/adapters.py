# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future import standard_library


standard_library.install_aliases()

from collective.collabora import utils
from collective.collabora.interfaces import IStoredFile
from plone.app.contenttypes.interfaces import IFile
from plone.namedfile.file import NamedBlobFile
from zope.component import adapter
from zope.interface import implementer


try:
    from Products.ATContentTypes.interfaces import IATFile
    from StringIO import StringIO  # py27 only
except ImportError:
    from collective.collabora.interfaces import IDummy as IATFile

    StringIO = utils.disallow


@adapter(IFile)
@implementer(IStoredFile)
class DXStoredFile(object):
    """Access the file storage on a Dexterity content object.

    By default that's the `file` attribute on the content object,
    but you can customize the field name.
    """

    # If you want to support a different file field, your subclass
    # only has to provide a different file_field_name
    file_field_name = "file"

    def __init__(self, context):
        self.context = context
        self.filename = context.file.filename
        self.contentType = context.file.contentType

    @property
    def file_field(self):
        return getattr(self.context, self.file_field_name)

    @file_field.setter
    def file_field(self, value):
        setattr(self.context, self.file_field_name, value)

    @property
    def data(self):
        return self.file_field.data

    @data.setter
    def data(self, data):
        self.file_field = NamedBlobFile(
            data=data, filename=self.filename, contentType=self.contentType
        )

    def getSize(self):
        return self.file_field.getSize()


@adapter(IATFile)
@implementer(IStoredFile)
class ATStoredFile(object):
    """Access the file storage on a Archetypes content object.

    By default that's the `file` File field on the content object,
    but you can customize the field name.
    """

    # If you want to support a different file field, your subclass
    # only has to provide a different file_field_name.
    file_field_name = "file"

    def __init__(self, context):
        self.context = context
        self.file_field = self.context.getField(self.file_field_name)
        if not self.file_field:
            raise AttributeError("Invalid file_field_name %r", self.file_field_name)
        # This weirdness is why we adopt the content type, rather than the blob
        # field directly - these accessors on the field need the parent context
        self.filename = self.file_field.getFilename(context)
        self.contentType = self.file_field.getContentType(context)

    @property
    def data(self):
        return self.context.data

    @data.setter
    def data(self, data):
        # This follows the README.txt in
        # https://github.com/plone/plone.app.blob/tree/master/src/plone/app/blob
        data_wrapper = StringIO(data)
        data_wrapper.filename = self.filename
        self.context.setFile(data_wrapper)

    def getSize(self):
        return self.file_field.get_size(self.context)
