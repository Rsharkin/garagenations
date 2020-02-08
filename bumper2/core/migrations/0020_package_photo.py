# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models.common
import services.s3.storage


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160420_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='photo',
            field=models.FileField(help_text=b'Photo of Package', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name),
        ),
    ]
