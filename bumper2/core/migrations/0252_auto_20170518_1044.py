# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0251_remove_item_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='workshop_asst_mgr',
            field=models.ForeignKey(related_name='booking_workshop_asst_mgr', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='workshop_asst_mgr',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='push_level',
            field=models.SmallIntegerField(default=1, null=True, blank=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral'), (6, b'RateUs'), (7, b'FillProfile'), (8, b'FillCarInfo'), (9, b'EOD'), (10, b'Req. Loc.')]),
        ),
    ]
