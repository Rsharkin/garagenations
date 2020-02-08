# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0145_auto_20161021_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opsalerttype',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
