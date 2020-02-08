# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0258_auto_20170711_1131'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workshopresources',
            old_name='for_date',
            new_name='on_date',
        ),
        migrations.AlterField(
            model_name='workshopresources',
            name='type_of_record',
            field=models.IntegerField(default=1, choices=[(1, b'Daily'), (2, b'Expected')]),
        ),
    ]
