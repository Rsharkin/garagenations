# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20160514_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercar',
            name='insurer',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usercar',
            name='insurer_due_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
