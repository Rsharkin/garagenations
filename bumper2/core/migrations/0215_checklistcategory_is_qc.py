# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0214_bookingchecklist_group_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklistcategory',
            name='is_qc',
            field=models.BooleanField(default=False),
        ),
    ]
