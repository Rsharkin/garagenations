# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0165_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='followup',
            name='follow_for',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'Workshop or customer?', choices=[(1, b'Customer'), (2, b'Workshop')]),
        ),
    ]
