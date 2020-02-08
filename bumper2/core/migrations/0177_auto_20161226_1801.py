# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0176_auto_20161226_1758'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalbookingimage',
            options={'ordering': ('-history_date', '-history_id'), 'get_latest_by': 'history_date', 'verbose_name': 'historical booking image'},
        ),
        migrations.AddField(
            model_name='bookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Sheet'), (3, b'Car Photo'), (4, b'Inspection Sheet')]),
        ),
        migrations.AddField(
            model_name='historicalbookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Sheet'), (3, b'Car Photo'), (4, b'Inspection Sheet')]),
        ),
        migrations.AlterField(
            model_name='bookingimage',
            name='booking',
            field=models.ForeignKey(related_name='booking_image', to='core.Booking'),
        ),
        migrations.AlterField(
            model_name='bookingimage',
            name='jobcard_type',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, b'Prepared By Driver'), (2, b'Prepared After Inspection'), (3, b'Prepared by Workshop')]),
        ),
        migrations.AlterField(
            model_name='bookingimage',
            name='media',
            field=models.ForeignKey(related_name='booking_image_media', to='core.Media'),
        ),
        migrations.AlterField(
            model_name='historicalbookingimage',
            name='jobcard_type',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, b'Prepared By Driver'), (2, b'Prepared After Inspection'), (3, b'Prepared by Workshop')]),
        ),
    ]
