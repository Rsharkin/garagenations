# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0260_workshopresources_updated_by'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='workshopresources',
            unique_together=set([('on_date', 'type_of_record')]),
        ),
    ]
