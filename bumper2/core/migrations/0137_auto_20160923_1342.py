# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0136_remove_carpanel_show_savings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carpanelprice',
            name='dealer_labour_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='dealer_material_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='dealer_part_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
    ]
