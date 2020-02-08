import uuid
import logging

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

logger = logging.getLogger(__name__)


def content_file_name(instance, original_filename):
    filename = str(uuid.uuid4())
    file_type = 'jpeg'
    if original_filename and str(original_filename).split('.'):
        file_type = str(original_filename).split('.')[-1]

    filename += '.' + file_type
    logger.info('old_file_name=%s to new_file_name=%s' % (original_filename, filename))
    return filename


@python_2_unicode_compatible
class CreatedAtAbstractBase(models.Model):
    """
        Stores the fields common to all incentive models
    """
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.id


@python_2_unicode_compatible
class Media(CreatedAtAbstractBase):
    MEDIA_TYPE_IMAGE = 'image'
    MEDIA_TYPE_VIDEO = 'video'
    MEDIA_TYPE_FILE = 'file'

    MEDIA_TYPES = (
        (MEDIA_TYPE_IMAGE, 'Image'),
        (MEDIA_TYPE_VIDEO, 'Video'),
        (MEDIA_TYPE_FILE, 'File'),
    )

    file = models.FileField(upload_to=content_file_name)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, null=True, blank=True)
    desc = models.CharField(max_length=64, null=True)
    filename = models.CharField(max_length=128, null=True, blank=True)
    content_type = models.CharField(max_length=50)
    size = models.IntegerField()
    uploaded_to_s3 = models.BooleanField(default=False)

    def __str__(self):
        return str(self.filename)


class Address(CreatedAtAbstractBase):
    address1 = models.CharField(max_length=1024)
    address2 = models.CharField(max_length=1024,null=True, blank=True, help_text="this field is updated from dashboard. "
                                                                     "Will be used to manually save address or landmark")
    pin_code = models.IntegerField(null=True)
    area = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128,null=True)
    state = models.CharField(max_length=128,null=True)
    country = models.CharField(max_length=128,null=True)
    latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True)
    longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True)

    def __str__(self):
        return self.address1

