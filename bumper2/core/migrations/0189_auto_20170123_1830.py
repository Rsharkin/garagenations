# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0188_auto_20170123_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingQualityChecks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_passed', models.BooleanField(default=False)),
                ('failure_reason', models.CharField(max_length=1024, null=True, blank=True)),
                ('booking', models.ForeignKey(related_name='booking_quality_check', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='qualitycheck',
            options={'verbose_name_plural': 'QualityChecks'},
        ),
        migrations.AlterModelOptions(
            name='qualitycheckcategory',
            options={'verbose_name_plural': 'QualityCheckCategories'},
        ),
        migrations.AlterField(
            model_name='bookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Crew To WS Sheet'), (4, b'Inspection Sheet'), (3, b'Car Photo'), (5, b'Handover WS To Crew Sheet'), (6, b'During Quality Check')]),
        ),
        migrations.AlterField(
            model_name='historicalbookingimage',
            name='image_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Jobcard'), (2, b'Handover Crew To WS Sheet'), (4, b'Inspection Sheet'), (3, b'Car Photo'), (5, b'Handover WS To Crew Sheet'), (6, b'During Quality Check')]),
        ),
        migrations.AlterField(
            model_name='qualitycheck',
            name='category',
            field=models.ForeignKey(related_name='quality_checks_list', to='core.QualityCheckCategory'),
        ),
        migrations.AddField(
            model_name='bookingqualitychecks',
            name='booking_image',
            field=models.ForeignKey(related_name='booking_qc_images', to='core.BookingImage', null=True),
        ),
        migrations.AddField(
            model_name='bookingqualitychecks',
            name='quality_check',
            field=models.ForeignKey(to='core.QualityCheck'),
        ),
    ]
