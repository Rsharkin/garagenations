# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0135_auto_20160924_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalAccounts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('phone', models.CharField(unique=True, max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
