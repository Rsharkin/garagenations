# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20160503_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billitem',
            name='bill',
            field=models.ForeignKey(related_name='bill_items', to='core.BookingBill'),
        ),
    ]
