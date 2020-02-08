# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0213_auto_20170223_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingchecklist',
            name='group_num',
            field=models.IntegerField(default=1),
        ),
    ]
