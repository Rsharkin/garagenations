# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0185_driverlocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAttendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attendance_type', models.PositiveSmallIntegerField(choices=[(1, b'Entry'), (2, b'Exit')])),
                ('track_date', models.DateField()),
                ('user', models.ForeignKey(related_name='user_attendance', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='driverlocation',
            name='direction',
            field=models.PositiveSmallIntegerField(choices=[(1, b'DriverToCustPick'), (2, b'CustToDriverPick'), (3, b'DriverToCustDrop'), (4, b'DriverCurrentLoc')]),
        ),
    ]
