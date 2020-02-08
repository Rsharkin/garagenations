# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from core.models.booking import Booking


def update_sources(apps, schema_editor):
    """
    For all booking sources, create a source.
    """
    Source = apps.get_model('core','Source')
    for idx,source in enumerate(Booking.BOOKING_SOURCES):
        Source.objects.create(source=source[0], order_num=idx, source_desc=source[1])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0178_workshop_is_doorstep'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('source_desc', models.CharField(max_length=128)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(update_sources, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.ForeignKey(related_name='booking_sources', db_column=b'source', blank=True, to='core.Source', null=True),
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial'), (b'drwheelz', b'drwheelz'), (b'incomingCall', b'Incoming Call'), (b'urbanClap', b'UrbanClap'), (b'cars24', b'Cars 24'), (b'hp', b'HP Petrol Pump')]),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='end_year',
            field=models.IntegerField(blank=True, null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017)]),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='start_year',
            field=models.IntegerField(blank=True, null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017)]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'source', db_constraint=False, blank=True, to='core.Source', null=True),
        ),
        migrations.AlterField(
            model_name='historicaluserinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial'), (b'drwheelz', b'drwheelz'), (b'incomingCall', b'Incoming Call'), (b'urbanClap', b'UrbanClap'), (b'cars24', b'Cars 24'), (b'hp', b'HP Petrol Pump')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(128, 128), (1, 1), (2, 2), (3, 3), (4, 4), (133, 133), (6, 6), (129, 129), (8, 8), (9, 9), (10, 10), (132, 132), (12, 12), (130, 130), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (131, 131), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (5, 5), (7, 7), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (23, 23), (19, 19), (25, 25), (13, 13), (56, 56), (24, 24), (216, 216), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127)]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='label',
            field=models.PositiveSmallIntegerField(help_text=b'This is to identify which screen will open in UI', null=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral'), (6, b'RateUs'), (7, b'FillProfile'), (8, b'FillCarInfo'), (9, b'EOD')]),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='push_level',
            field=models.SmallIntegerField(default=1, null=True, blank=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral'), (6, b'RateUs'), (7, b'FillProfile'), (8, b'FillCarInfo'), (9, b'EOD')]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial'), (b'drwheelz', b'drwheelz'), (b'incomingCall', b'Incoming Call'), (b'urbanClap', b'UrbanClap'), (b'cars24', b'Cars 24'), (b'hp', b'HP Petrol Pump')]),
        ),
    ]
