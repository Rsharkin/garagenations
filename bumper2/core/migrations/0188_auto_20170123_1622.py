# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0187_auto_20170120_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualityCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quality_check', models.CharField(max_length=512)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QualityCheckCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='qualitycheck',
            name='category',
            field=models.ForeignKey(related_name='qc_category', to='core.QualityCheckCategory'),
        ),
    ]
