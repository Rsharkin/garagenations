# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20160419_1952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workshopholiday',
            old_name='date',
            new_name='holiday_date',
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='end_year',
            field=models.IntegerField(blank=True, null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016)]),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='start_year',
            field=models.IntegerField(blank=True, null=True, choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016)]),
        ),
        migrations.AlterField(
            model_name='carmodelversionname',
            name='car_model_version',
            field=models.ForeignKey(to='core.CarModelVersion'),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='close_at',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='off_days',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=13, null=True, choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')]),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='open_at',
            field=models.TimeField(),
        ),
    ]
