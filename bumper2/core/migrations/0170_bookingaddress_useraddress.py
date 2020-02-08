# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0169_auto_20161203_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingaddress',
            name='useraddress',
            field=models.ForeignKey(blank=True, to='core.UserAddress', null=True),
        ),
    ]
