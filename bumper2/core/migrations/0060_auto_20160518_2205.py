# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_useremailverify'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='vendor',
            field=models.CharField(default=b'Citrus', max_length=16, null=True, blank=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='vendor',
            field=models.CharField(default=b'Citrus', max_length=16, null=True, blank=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')]),
        ),
    ]
