# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.s3.storage
import core.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20161117_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanelprice',
            name='big_photo',
            field=models.FileField(help_text=b'Panel of the car shown on detail page', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name, blank=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='photo',
            field=models.FileField(help_text=b'Panel of the car shown on list page', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')]),
        ),
    ]
