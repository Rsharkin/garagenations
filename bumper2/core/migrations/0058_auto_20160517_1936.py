# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.s3.storage
import core.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20160517_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_doorstep',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carpanel',
            name='big_photo',
            field=models.FileField(default='4f043bb9-9fdd-44ed-bf8a-bf0eab917885.jpg', help_text=b'Panel of the car shown on detail page', storage=services.s3.storage.S3Storage(), upload_to=core.models.common.content_file_name),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='is_doorstep',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='carpanel',
            name='photo',
            field=models.FileField(help_text=b'Panel of the car shown on list page', storage=services.s3.storage.S3Storage(), upload_to=core.models.common.content_file_name),
        ),
    ]
