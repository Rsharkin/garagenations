# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratch(es)'), (2, b'Remove Dent(s) and Scratch(es)'), (3, b'Replace Panel'), (4, b'Paint Only')]),
        ),
    ]
