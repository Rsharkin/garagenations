# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_historicalbookingcoupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='website_url',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
