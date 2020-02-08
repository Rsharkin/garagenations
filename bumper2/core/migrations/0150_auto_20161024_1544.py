# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0149_auto_20161021_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='labour_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='material_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='part_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='labour_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='material_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='part_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingpackagepanel',
            name='labour_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingpackagepanel',
            name='material_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingpackagepanel',
            name='part_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingpackagepanel',
            name='price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='itemprice',
            name='price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
    ]
