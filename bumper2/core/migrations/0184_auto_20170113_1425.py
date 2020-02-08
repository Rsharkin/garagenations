# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0183_auto_20170110_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='followupresult',
            name='notification',
            field=models.ForeignKey(blank=True, to='core.Notifications', null=True),
        ),
        migrations.AlterField(
            model_name='bookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Crew To WS Sheet'), (4, b'Inspection Sheet'), (3, b'Car Photo'), (5, b'Handover WS To Crew Sheet')]),
        ),
        migrations.AlterField(
            model_name='historicalbookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Crew To WS Sheet'), (4, b'Inspection Sheet'), (3, b'Car Photo'), (5, b'Handover WS To Crew Sheet')]),
        ),
    ]
