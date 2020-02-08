# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0258_auto_20170714_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='bumperuser',
            name='signup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='colors',
            field=models.ManyToManyField(to='core.CarColor', blank=True),
        ),
    ]
