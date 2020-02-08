# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0267_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carmodelvariant',
            options={},
        ),
        migrations.AddField(
            model_name='carmodel',
            name='variants',
            field=models.ManyToManyField(to='core.CarModelVariant', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='carmodelvariant',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='carmodelvariant',
            name='car_model',
        ),
    ]
