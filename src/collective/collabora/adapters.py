from future import standard_library

standard_library.install_aliases()

from collective.collabora.interfaces import IStoredFile
from plone.app.contenttypes.interfaces import IFile
from plone.namedfile.file import NamedBlobFile
from zope.component import adapter
from zope.interface import implementer


@adapter(IFile)
@implementer(IStoredFile)
class DXStoredFile:
    """Access the file storage on a Dexterity content object.

    By default that's the `file` attribute on the content object,
    but you can customize the field name.
    """

    # If you want to support a different file field, your subclass
    # only has to provide a different file_field_name
    file_field_name = "file"

    def __init__(self, context):
        self.context = context
        self.filename = self.file_field.filename
        self.contentType = self.file_field.contentType

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
