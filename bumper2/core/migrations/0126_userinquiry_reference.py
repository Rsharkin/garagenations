# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0125_followup_next_followup_dt'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinquiry',
            name='reference',
            field=models.CharField(max_length=1048, null=True, blank=True),
        ),
    ]
