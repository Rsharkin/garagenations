# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_auto_20160731_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(related_name='booking_payment', blank=True, to='core.Booking', null=True),
        ),
    ]
