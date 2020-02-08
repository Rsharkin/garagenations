# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0155_auto_20161108_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowupResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('action_type', models.PositiveSmallIntegerField(choices=[(1, b'Followup'), (2, b'Assigned')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='followup',
            name='tags',
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')]),
        ),
        migrations.DeleteModel(
            name='FollowupTag',
        ),
        migrations.AddField(
            model_name='followup',
            name='result',
            field=models.ForeignKey(blank=True, to='core.FollowupResult', null=True),
        ),
    ]
