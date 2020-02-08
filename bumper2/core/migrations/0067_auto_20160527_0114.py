# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20160527_0106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notifications',
            old_name='use_template',
            new_name='use_file_template',
        ),
    ]
