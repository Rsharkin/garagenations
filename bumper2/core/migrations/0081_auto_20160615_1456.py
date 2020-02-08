# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_bookingjobcard'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalBookingJobcard',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('jobcard_type', models.PositiveSmallIntegerField(choices=[(1, b'Prepared By Driver'), (2, b'Prepared After Inspection'), (3, b'Prepared by Workshop')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Booking', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('media', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Media', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking jobcard',
            },
        ),
        migrations.AlterField(
            model_name='bookingjobcard',
            name='jobcard_type',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Prepared By Driver'), (2, b'Prepared After Inspection'), (3, b'Prepared by Workshop')]),
        ),
        migrations.AlterField(
            model_name='historicalpayment',
            name='vendor',
            field=models.CharField(blank=True, max_length=16, null=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='vendor',
            field=models.CharField(blank=True, max_length=16, null=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')]),
        ),
    ]
