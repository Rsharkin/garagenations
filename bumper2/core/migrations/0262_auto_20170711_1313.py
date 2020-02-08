# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0261_auto_20170711_1308'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='workshopresources',
            unique_together=set([('workshop', 'on_date', 'type_of_record')]),
        ),
    ]
