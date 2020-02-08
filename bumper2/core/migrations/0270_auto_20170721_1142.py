# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0269_auto_20170719_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carmodelvariant',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
