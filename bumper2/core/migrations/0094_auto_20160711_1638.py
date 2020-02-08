# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0093_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='labour_kk_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='labour_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='labour_sb_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='labour_service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='material_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='material_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='part_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='part_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
