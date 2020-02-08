# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0113_carpanelprice_internal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinquiry',
            name='read',
        ),
    ]
