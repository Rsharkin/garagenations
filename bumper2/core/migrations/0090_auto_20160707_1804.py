# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_auto_20160707_1801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnerlead',
            name='car',
        ),
        migrations.AlterField(
            model_name='partnerlead',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
