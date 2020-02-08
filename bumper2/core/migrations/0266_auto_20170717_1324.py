# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0265_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpartquote',
            name='selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalbookingpartquote',
            name='selected',
            field=models.BooleanField(default=False),
        ),
    ]
