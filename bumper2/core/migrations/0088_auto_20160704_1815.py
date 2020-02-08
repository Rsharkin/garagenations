# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_auto_20160624_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address2',
            field=models.CharField(help_text=b'this field is updated from dashboard. Will be used to manually save address or landmark', max_length=1024, null=True, blank=True),
        ),
    ]
