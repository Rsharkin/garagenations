# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0180_auto_20170102_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='booking',
            field=models.ForeignKey(related_name='message_booking', blank=True, to='core.Booking', null=True),
        ),
    ]
