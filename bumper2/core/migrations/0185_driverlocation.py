# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0184_auto_20170113_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('latitude', models.DecimalField(max_digits=11, decimal_places=8)),
                ('longitude', models.DecimalField(max_digits=11, decimal_places=8)),
                ('direction', models.PositiveSmallIntegerField(choices=[(1, b'DriverToCustPick'), (2, b'CustToDriverPick'), (3, b'DriverToCustDrop')])),
                ('track_time', models.DateTimeField()),
                ('driver', models.ForeignKey(related_name='location_driver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
