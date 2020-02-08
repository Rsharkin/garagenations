# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0076_auto_20160610_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('show_to_user', models.BooleanField(default=False, verbose_name='Show to User')),
                ('city', models.ManyToManyField(to='core.City', verbose_name='City')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('value', models.IntegerField(help_text='Arbitrary coupon value', verbose_name='Value')),
                ('code', models.CharField(max_length=30, blank=True, help_text='Leaving this field empty will generate a random code.', unique=True, verbose_name='Code', db_index=True)),
                ('desc', models.CharField(max_length=255, verbose_name='Description')),
                ('type', models.CharField(max_length=20, verbose_name='Type', choices=[(b'monetary', b'Money based coupon'), (b'percentage', b'Percentage discount')])),
                ('valid_until', models.DateTimeField(help_text='Leave empty for coupons that never expire', null=True, verbose_name='Valid until', blank=True)),
                ('applicable_to', multiselectfield.db.fields.MultiSelectField(max_length=20, verbose_name='Applicable To', choices=[(1, b'Applicable to Part price'), (2, b'Applicable to Material price'), (3, b'Applicable to Labour price'), (4, b'Applicable to Full Bill')])),
                ('used_times', models.IntegerField(default=0, help_text='How many times this coupon can be used PER USER? 0 means infinite times', verbose_name='Used Times')),
                ('max_use', models.IntegerField(default=0, help_text='How many times this coupon can be used? 0 means infinite times', verbose_name='Max Use')),
                ('amount_limit', models.IntegerField(help_text='For Percentage discount, this is the amount limit for which coupon can be used', null=True, verbose_name='Limit', blank=True)),
                ('cashback_value', models.IntegerField(default=0, help_text='Cashback Value for coupon with cashback. 0 means no cashback entry.', verbose_name='Cashback Value')),
                ('cashback_type', models.CharField(choices=[(b'monetary', b'Money based coupon'), (b'percentage', b'Percentage discount')], max_length=20, blank=True, help_text='Mandatory if cashback value', null=True, verbose_name='Cashback Type')),
                ('cashback_amt_limit', models.IntegerField(help_text='For Percentage cashback, this is the amount limit for which coupon can be used', null=True, verbose_name='Cashback Limit', blank=True)),
                ('cashback_applicable_to', multiselectfield.db.fields.MultiSelectField(default=4, max_length=20, verbose_name='Cashback Applicable To', choices=[(1, b'Applicable to Part price'), (2, b'Applicable to Material price'), (3, b'Applicable to Labour price'), (4, b'Applicable to Full Bill')])),
                ('how_it_works', models.CharField(max_length=255, null=True, verbose_name='How It Works', blank=True)),
                ('title', models.CharField(max_length=64, verbose_name='Title')),
                ('campaign', models.ForeignKey(related_name='couponscampaign', verbose_name='Campaign', blank=True, to='core.Campaign', null=True)),
                ('packages', models.ManyToManyField(related_name='coupon_packages', to='core.Package')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='You may specify a user you want to restrict this coupon to.', null=True, verbose_name='User')),
            ],
            options={
                'ordering': ['created_at'],
                'verbose_name': 'Coupon',
                'verbose_name_plural': 'Coupons',
            },
        ),
        migrations.CreateModel(
            name='CouponUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discount', models.DecimalField(default=0, help_text='This is the cash discount given for coupon.', max_digits=10, decimal_places=2)),
                ('cashback', models.DecimalField(default=0, help_text='This is the cashback given for coupon.', max_digits=10, decimal_places=2)),
                ('is_paid', models.BooleanField(default=False, help_text='Coupon will be used only if payment is made.')),
                ('booking', models.ForeignKey(to='core.Booking')),
                ('coupon', models.ForeignKey(to='core.Coupon')),
            ],
            options={
                'verbose_name': 'CouponUse',
                'verbose_name_plural': 'CouponUses',
            },
        ),
    ]
