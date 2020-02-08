# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0208_auto_20170210_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carmodelversionname',
            name='car_model_version',
        ),
        migrations.AddField(
            model_name='carmodelversion',
            name='name',
            field=models.CharField(default='VXI', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='carmodelversion',
            name='car_model',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='carmodelversion',
            unique_together=set([]),
        ),
        migrations.DeleteModel(
            name='CarModelVersionName',
        ),
        migrations.RemoveField(
            model_name='carmodelversion',
            name='cc',
        ),
        migrations.RemoveField(
            model_name='carmodelversion',
            name='fuel',
        ),
        migrations.RemoveField(
            model_name='carmodelversion',
            name='gear',
        ),
        migrations.RemoveField(
            model_name='carmodelversion',
            name='seating_capacity',
        ),
    ]
