# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20160510_1822'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookingstatus',
            old_name='status_category',
            new_name='category',
        ),
    ]
