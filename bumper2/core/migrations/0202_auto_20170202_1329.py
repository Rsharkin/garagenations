# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0201_auto_20170202_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookinghandoveritem',
            name='group',
        ),
        migrations.AddField(
            model_name='bookinghandoveritem',
            name='ops_status',
            field=models.ForeignKey(default=1, to='core.BookingOpsStatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookinghandoveritem',
            name='status',
            field=models.ForeignKey(default=1, to='core.BookingStatus'),
            preserve_default=False,
        ),
    ]
