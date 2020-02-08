# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0166_followup_follow_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingproformainvoice',
            name='note',
            field=models.CharField(default='', max_length=2048),
            preserve_default=False,
        ),
    ]
