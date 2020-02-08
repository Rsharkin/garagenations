# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20160510_1619'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusCategory',
            fields=[
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('category', models.CharField(unique=True, max_length=128)),
                ('flow_order_num', models.SmallIntegerField(default=1)),
            ],
            options={
                'ordering': ['flow_order_num'],
                'verbose_name_plural': 'Status Categories',
            },
        ),
        migrations.RemoveField(
            model_name='bookingstatus',
            name='category',
        ),
        migrations.AddField(
            model_name='bookingstatus',
            name='status_category',
            field=models.ForeignKey(blank=True, to='core.StatusCategory', null=True),
        ),
    ]
