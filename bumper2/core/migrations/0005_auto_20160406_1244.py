# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.s3.storage
import core.models.common


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_booking_messages_messageuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('logo', models.FileField(help_text=b'Logo of the brand', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('start_year', models.IntegerField(null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016)])),
                ('end_year', models.IntegerField(null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016)])),
                ('photo', models.FileField(help_text=b'Photo of the car', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name)),
                ('car_type', models.SmallIntegerField(default=1, choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')])),
                ('active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(related_name='carmodel', to='core.CarBrand')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CarModelVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cc', models.IntegerField(null=True, blank=True)),
                ('fuel', models.CharField(max_length=20, choices=[(b'Petrol', b'Petrol'), (b'Diesel', b'Diesel'), (b'CNG', b'CNG'), (b'LPG', b'LPG'), (b'Electric', b'Electric'), (b'Hybrid', b'Hybrid')])),
                ('gear', models.CharField(max_length=20, choices=[(b'Manual', b'Manual'), (b'Automatic', b'Automatic')])),
                ('seating_capacity', models.SmallIntegerField()),
                ('active', models.BooleanField(default=True)),
                ('car_model', models.ForeignKey(related_name='carversion', to='core.CarModel')),
            ],
            options={
                'ordering': ['car_model__name'],
            },
        ),
        migrations.CreateModel(
            name='CarModelVersionName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('active', models.BooleanField(default=True)),
                ('car_model_version', models.ForeignKey(to='core.CarModelVersion', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='carmodelversion',
            unique_together=set([('car_model', 'cc', 'fuel', 'gear', 'seating_capacity')]),
        ),
        migrations.AlterUniqueTogether(
            name='carmodel',
            unique_together=set([('brand', 'name', 'start_year', 'end_year')]),
        ),
    ]
