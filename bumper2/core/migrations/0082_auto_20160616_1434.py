# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_auto_20160615_1456'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-id']},
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='labour_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='labour_service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='material_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='material_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='part_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='part_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='labour_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='labour_service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='material_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='material_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='part_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='part_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='labour_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='material_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='part_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='labour_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='labour_service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='material_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='material_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='part_price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='part_vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='labour_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='packageprice',
            name='material_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='packageprice',
            name='part_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coupon',
            name='applicable_to',
            field=multiselectfield.db.fields.MultiSelectField(max_length=20, verbose_name='Applicable To', choices=[(1, b'Applicable to Part price'), (2, b'Applicable to Material price'), (3, b'Applicable to Labour price')]),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='cashback_applicable_to',
            field=multiselectfield.db.fields.MultiSelectField(max_length=20, verbose_name='Cashback Applicable To', choices=[(1, b'Applicable to Part price'), (2, b'Applicable to Material price'), (3, b'Applicable to Labour price')]),
        ),
    ]
