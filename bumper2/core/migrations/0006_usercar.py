# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20160406_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('registration_number', models.CharField(max_length=13, null=True, blank=True)),
                ('purchased_on', models.DateField(null=True, blank=True)),
                ('color', models.CharField(max_length=32, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('car_model', models.ForeignKey(to='core.CarModel')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
