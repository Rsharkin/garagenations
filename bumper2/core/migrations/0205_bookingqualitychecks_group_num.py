# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0204_creditmemo_historicalcreditmemo'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingqualitychecks',
            name='group_num',
            field=models.IntegerField(default=1),
        ),
    ]
