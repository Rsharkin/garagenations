# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0150_auto_20161024_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingCustFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer_care', models.PositiveSmallIntegerField(choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')])),
                ('work_quality', models.PositiveSmallIntegerField(choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')])),
                ('value_for_money', models.PositiveSmallIntegerField(choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')])),
                ('any_suggestions', models.CharField(max_length=2048, null=True, blank=True)),
                ('booking', models.ForeignKey(related_name='booking_cust_feedback', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
