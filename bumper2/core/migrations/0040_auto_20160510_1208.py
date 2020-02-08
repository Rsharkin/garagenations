# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160509_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingstatus',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='bookingsubstatus',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
