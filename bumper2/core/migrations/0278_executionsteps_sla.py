# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0277_executionsteps_sla_stepsofwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='executionsteps',
            name='sla',
            field=models.ForeignKey(default=1, to='core.Sla'),
            preserve_default=False,
        ),
    ]
