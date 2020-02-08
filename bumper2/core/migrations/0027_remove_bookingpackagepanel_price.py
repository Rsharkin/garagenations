# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20160429_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='price',
        ),
    ]
