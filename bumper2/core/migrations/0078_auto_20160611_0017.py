# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_campaign_coupon_couponuse'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingCoupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discount', models.DecimalField(default=0, help_text='This is the cash discount given for coupon.', max_digits=10, decimal_places=2)),
                ('cashback', models.DecimalField(default=0, help_text='This is the cashback given for coupon.', max_digits=10, decimal_places=2)),
                ('is_paid', models.BooleanField(default=False, help_text='Coupon will be used only if payment is made.')),
                ('booking', models.ForeignKey(related_name='booking_coupon', to='core.Booking')),
                ('coupon', models.ForeignKey(to='core.Coupon')),
            ],
            options={
                'verbose_name': 'BookingCoupon',
                'verbose_name_plural': 'BookingCoupons',
            },
        ),
        migrations.RemoveField(
            model_name='couponuse',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='couponuse',
            name='coupon',
        ),
        migrations.DeleteModel(
            name='CouponUse',
        ),
    ]
