# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_userauthcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDevices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device_id', models.CharField(help_text=b'This stores gcm id or apns and is used as alternate to device id to uniquely identify device', max_length=512, null=True)),
                ('device_type', models.CharField(default=b'android', max_length=7, choices=[(b'android', b'android'), (b'ios', b'ios')])),
                ('device_info', models.CharField(max_length=128, null=True)),
                ('device_os_version', models.CharField(max_length=16, null=True)),
                ('app_version', models.DecimalField(default=1.0, null=True, max_digits=6, decimal_places=2)),
                ('is_dev', models.BooleanField(default=False)),
                ('gcm_device_id', models.IntegerField(null=True)),
                ('apns_device_id', models.IntegerField(null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
