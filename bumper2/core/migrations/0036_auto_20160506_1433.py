# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20160503_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingstatus',
            name='status',
            field=models.CharField(unique=True, max_length=128),
        ),
    ]
