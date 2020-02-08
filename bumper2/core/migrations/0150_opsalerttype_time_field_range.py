# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0149_auto_20161021_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='opsalerttype',
            name='time_field_range',
            field=models.BooleanField(default=False, help_text=b'this tells whether the time_field is range.'),
        ),
    ]
