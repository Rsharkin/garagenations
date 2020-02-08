# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0256_auto_20170701_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='utm_campaign',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='utm_medium',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='utm_source',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='utm_campaign',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='utm_medium',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='utm_source',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingreworkpackagepanel',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Fix Rusted Area'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')]),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Fix Rusted Area'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')]),
        ),
    ]
