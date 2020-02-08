# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='workshop',
            field=models.ForeignKey(to='core.Workshop', null=True),
        ),
    ]
