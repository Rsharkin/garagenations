# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160331_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=core.models.common.content_file_name)),
                ('media_type', models.CharField(blank=True, max_length=10, null=True, choices=[(b'image', b'Image'), (b'video', b'Video'), (b'file', b'File')])),
                ('desc', models.CharField(max_length=64, null=True)),
                ('filename', models.CharField(max_length=128)),
                ('content_type', models.CharField(max_length=50)),
                ('size', models.IntegerField()),
                ('uploaded_to_s3', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
