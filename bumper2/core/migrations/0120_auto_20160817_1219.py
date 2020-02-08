# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0119_remove_followup_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinquiry',
            name='email',
        ),
        migrations.RemoveField(
            model_name='userinquiry',
            name='name',
        ),
        migrations.RemoveField(
            model_name='userinquiry',
            name='phone',
        ),
    ]
