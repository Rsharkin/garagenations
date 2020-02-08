# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0240_auto_20170421_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referralcampaign',
            name='flow',
            field=models.CharField(help_text='Do not change this after creation. It is used in code', max_length=32, verbose_name='Flow'),
        ),
    ]
