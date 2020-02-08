# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackage',
            name='labour_kk_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='labour_sb_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='labour_kk_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='labour_sb_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='labour_kk_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='labour_sb_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
