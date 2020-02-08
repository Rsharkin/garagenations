# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0205_bookingqualitychecks_group_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingcustfeedback',
            name='booking_experience',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')]),
        ),
        migrations.AddField(
            model_name='bookingcustfeedback',
            name='pickup_experience',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')]),
        ),
        migrations.AlterField(
            model_name='bookingcustfeedback',
            name='customer_care',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')]),
        ),
        migrations.AlterField(
            model_name='bookingcustfeedback',
            name='value_for_money',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')]),
        ),
        migrations.AlterField(
            model_name='bookingcustfeedback',
            name='work_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Very UnHappy'), (2, b'UnHappy'), (3, b'Neutral'), (4, b'Happy'), (5, b'Very Happy')]),
        ),
    ]
