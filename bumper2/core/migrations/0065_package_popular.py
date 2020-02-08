# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_auto_20160523_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='popular',
            field=models.BooleanField(default=False),
        ),
    ]
