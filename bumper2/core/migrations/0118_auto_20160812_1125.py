# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import migrations
from core.models.booking import Booking

def update_booking_followups(apps, schema_editor):
    """
    For all bookings, update the intermediate table BookingFollowup for old entries.
    """
    booking_followups = []
    BookingFollowup = Booking.followup.through
    bookings = Booking.objects.all()
    Followup = apps.get_model('core','Followup')
    for b in bookings:
        followups = Followup.objects.filter(booking=b.id)
        for f in followups:
            booking_followups.append(BookingFollowup(booking=b,followup_id=f.id))
    BookingFollowup.objects.bulk_create(booking_followups)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0117_auto_20160812_1124'),
    ]

    operations = [
        migrations.RunPython(update_booking_followups, reverse_code=migrations.RunPython.noop),
    ]
