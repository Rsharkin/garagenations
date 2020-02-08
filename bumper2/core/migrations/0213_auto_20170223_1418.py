# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0212_auto_20170220_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('has_issue', models.BooleanField(default=False)),
                ('is_applicable', models.BooleanField(default=True)),
                ('reason_text', models.TextField(null=True, blank=True)),
                ('booking', models.ForeignKey(related_name='booking_checklist', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChecklistCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Checklist Categories',
            },
        ),
        migrations.CreateModel(
            name='ChecklistItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('item_type', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Boolean'), (2, b'Image')])),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
                ('category', models.ForeignKey(to='core.ChecklistCategory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(128, 128), (1, 1), (2, 2), (3, 3), (4, 4), (133, 133), (6, 6), (129, 129), (8, 8), (9, 9), (10, 10), (132, 132), (12, 12), (130, 130), (142, 142), (15, 15), (141, 141), (145, 145), (18, 18), (131, 131), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (154, 154), (5, 5), (134, 134), (135, 135), (136, 136), (51, 51), (52, 52), (53, 53), (54, 54), (137, 137), (23, 23), (7, 7), (58, 58), (59, 59), (138, 138), (19, 19), (139, 139), (25, 25), (140, 140), (106, 106), (55, 55), (13, 13), (56, 56), (14, 14), (24, 24), (216, 216), (143, 143), (17, 17), (16, 16), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (144, 144), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127)]),
        ),
        migrations.AddField(
            model_name='bookingchecklist',
            name='item',
            field=models.ForeignKey(to='core.ChecklistItem'),
        ),
        migrations.AddField(
            model_name='bookingchecklist',
            name='media',
            field=models.ManyToManyField(related_name='checklist_img', to='core.Media'),
        ),
        migrations.AddField(
            model_name='bookingchecklist',
            name='ops_status',
            field=models.ForeignKey(to='core.BookingOpsStatus'),
        ),
        migrations.AddField(
            model_name='bookingchecklist',
            name='status',
            field=models.ForeignKey(to='core.BookingStatus'),
        ),
        migrations.AddField(
            model_name='bookingchecklist',
            name='updated_by',
            field=models.ForeignKey(related_name='bchecklist_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
