# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20161117_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityChangeTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.SmallIntegerField(choices=[(1, b'Booking'), (2, b'User')])),
                ('content_id', models.IntegerField()),
                ('item_tracked', models.CharField(help_text=b'Column name if tracking a columnotherwise action ', max_length=64)),
                ('change_type', models.SmallIntegerField(choices=[(1, b'Updated'), (2, b'Not Updated')])),
                ('old_value', models.CharField(max_length=1024, null=True, blank=True)),
                ('new_value', models.CharField(max_length=1024, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'EntityChangeTracker',
            },
        ),
    ]
