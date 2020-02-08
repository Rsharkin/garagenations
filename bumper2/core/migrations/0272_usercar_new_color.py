# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0271_auto_20170725_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercar',
            name='new_color',
            field=models.ForeignKey(blank=True, to='core.CarColor', null=True),
        ),
    ]
