# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0132_auto_20160919_1142'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bumper_app', models.PositiveSmallIntegerField(choices=[(1, b'Not Happy'), (2, b'Loved It')])),
                ('customer_care', models.PositiveSmallIntegerField(choices=[(1, b'Not Happy'), (2, b'Loved It')])),
                ('work_quality', models.PositiveSmallIntegerField(choices=[(1, b'Not Happy'), (2, b'Loved It')])),
                ('value_for_money', models.PositiveSmallIntegerField(choices=[(1, b'Not Happy'), (2, b'Loved It')])),
                ('pick_drop_service', models.PositiveSmallIntegerField(choices=[(1, b'Not Happy'), (2, b'Loved It')])),
                ('wow_moment', models.CharField(max_length=2048)),
                ('any_suggestions', models.CharField(max_length=2048)),
                ('feedback_remarks', models.CharField(max_length=2048)),
                ('customer_issue', models.CharField(max_length=2048)),
                ('referrals', models.CharField(max_length=2048, null=True, blank=True)),
                ('experience_rating', models.PositiveSmallIntegerField()),
                ('booking', models.ForeignKey(related_name='booking_feedback', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (23, 23), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (216, 216), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (24, 24), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (17, 17), (107, 107), (108, 108), (109, 109), (111, 111), (51, 51), (25, 25), (52, 52), (106, 106)]),
        ),
    ]
