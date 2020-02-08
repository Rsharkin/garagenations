# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0154_auto_20161106_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='workshop_eta',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='workshop_eta',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
