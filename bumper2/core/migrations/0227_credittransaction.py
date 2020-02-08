# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0226_auto_20170315_1242'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('trans_type', models.PositiveSmallIntegerField(verbose_name='Transaction Type', choices=[(1, b'CREDIT'), (2, b'DEBIT')])),
                ('entity', models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'Referral', b'Referral')])),
                ('entity_id', models.IntegerField(null=True, blank=True)),
                ('reason', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Credit Transaction',
                'verbose_name_plural': 'Credit Transactions',
            },
        ),
    ]
