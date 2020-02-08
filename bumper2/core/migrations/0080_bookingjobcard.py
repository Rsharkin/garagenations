# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingJobcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('jobcard_type', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)])),
                ('booking', models.ForeignKey(related_name='booking_jobcard', to='core.Booking')),
                ('media', models.ForeignKey(related_name='jobcard_media', to='core.Media')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
