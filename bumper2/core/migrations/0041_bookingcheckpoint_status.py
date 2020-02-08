# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20160510_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingcheckpoint',
            name='status',
            field=models.ForeignKey(default=1, to='core.BookingStatus'),
            preserve_default=False,
        ),
    ]
