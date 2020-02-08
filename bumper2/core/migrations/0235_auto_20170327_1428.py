# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0234_auto_20170324_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingimage',
            name='details',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookingimage',
            name='ops_status',
            field=models.ForeignKey(blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.AddField(
            model_name='bookingimage',
            name='status',
            field=models.ForeignKey(blank=True, to='core.BookingStatus', null=True),
        ),
        migrations.AddField(
            model_name='bookingimage',
            name='updated_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingimage',
            name='details',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbookingimage',
            name='ops_status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingimage',
            name='status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingStatus', null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingimage',
            name='updated_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
