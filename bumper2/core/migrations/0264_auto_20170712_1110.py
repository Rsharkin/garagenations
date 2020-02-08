# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0263_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpartdoc',
            name='final_price_cust',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='bookingpartdoc',
            name='mrp',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='bookingpartdoc',
            name='net_dealer_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpartdoc',
            name='final_price_cust',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpartdoc',
            name='mrp',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpartdoc',
            name='net_dealer_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingpartquote',
            name='notes',
            field=models.ManyToManyField(to='core.PartQuoteNote'),
        ),
    ]
