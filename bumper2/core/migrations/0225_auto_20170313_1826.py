# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0224_auto_20170313_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountReasons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bookingdiscount',
            name='reason_dd',
            field=models.ForeignKey(blank=True, to='core.DiscountReasons', null=True),
        ),
    ]
