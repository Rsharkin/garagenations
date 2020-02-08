# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_auto_20160513_0305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='to',
            field=models.CharField(help_text=b'Emails comma separated, For SMS this will be phone number without +91.', max_length=64, null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='bookingpackage',
            unique_together=set([('booking', 'package')]),
        ),
        migrations.AlterUniqueTogether(
            name='bookingpackagepanel',
            unique_together=set([('booking_package', 'panel')]),
        ),
    ]
