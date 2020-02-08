# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0226_auto_20170315_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingchecklist',
            name='ops_status',
            field=models.ForeignKey(blank=True, to='core.BookingOpsStatus', null=True),
        ),
    ]
