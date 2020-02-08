# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_auto_20160607_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace Panel'), (4, b'Paint Only')]),
        ),
    ]
