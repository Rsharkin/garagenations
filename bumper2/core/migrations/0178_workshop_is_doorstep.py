# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0177_auto_20161226_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshop',
            name='is_doorstep',
            field=models.BooleanField(default=False),
        ),
    ]
