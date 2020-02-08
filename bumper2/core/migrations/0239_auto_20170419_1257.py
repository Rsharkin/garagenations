# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0238_auto_20170419_1229'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bookingflag',
            unique_together=set([('booking', 'flag_type')]),
        ),
    ]
