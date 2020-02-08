# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0135_auto_20160923_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carpanel',
            name='show_savings',
        ),
    ]
