# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0167_bookingproformainvoice_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingproformainvoice',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pending'), (2, b'Cancelled'), (3, b'Paid')]),
        ),
    ]
