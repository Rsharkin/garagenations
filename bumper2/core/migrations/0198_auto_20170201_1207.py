# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0197_teamalert_resolved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamalert',
            name='reason_text',
            field=models.TextField(null=True, blank=True),
        ),
    ]
