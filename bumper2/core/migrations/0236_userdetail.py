# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0235_auto_20170327_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('imei_no', models.CharField(help_text=b'IMEI number of device used by user.', max_length=16, null=True, blank=True)),
                ('cre_id', models.CharField(help_text=b'CRE ID from Ninja CRM', max_length=16, null=True, blank=True)),
                ('user', models.OneToOneField(related_name='user_detail', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
