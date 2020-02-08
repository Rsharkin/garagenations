# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0243_remove_referral_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='carmodel',
            name='parent',
            field=models.ForeignKey(blank=True, to='core.CarModel', null=True),
        ),
        migrations.AddField(
            model_name='usercar',
            name='year',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
