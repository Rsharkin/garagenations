# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackage',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
