"""
    Caller assignment
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.users import Caller, UserInquiry
from core.models.booking import Booking
import logging
import itertools
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: CALLER_ASSIGNMENT:: Caller assignment for bookings and user inquiries"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: CALLER_ASSIGNMENT:: Script started - current_time: %s" % current_time)
        last_call_booking_caller = Caller.objects.filter(last_call_booking=True).first()
        last_booking_caller_order = 1
        if last_call_booking_caller:
            last_booking_caller_order = last_call_booking_caller.sort_order
        bookings = Booking.objects.filter(caller__isnull=True)
        booking_callers = Caller.objects.filter(sort_order__gt=last_booking_caller_order).order_by('sort_order') | Caller.objects.filter(sort_order__lte=last_booking_caller_order).order_by('sort_order')
        if not bookings:
            logger.info("Script:: CALLER_ASSIGNMENT:: No bookings to assign caller to")
        prev_caller = None

        # max_booking_count = max([caller.assigned_bookings_count for caller in booking_callers])
        # min_booking_count = min([caller.assigned_bookings_count for caller in booking_callers])

        for booking, caller in itertools.izip(bookings,itertools.cycle(booking_callers)):
            try:
                booking.caller = caller.user
                booking.save()
                if prev_caller:
                    prev_caller.last_call_booking = False
                    prev_caller.save()
                caller.last_call_booking = True
                caller.save()
                prev_caller = caller
            except:
                logger.exception("Script:: CALLER_ASSIGNMENT:: Error assigning caller for booking: %s", booking.id)

        last_call_ui_caller = Caller.objects.filter(last_call_inquiry=True).first()
        last_ui_caller_order = 1
        if last_call_ui_caller:
            last_ui_caller_order = last_call_ui_caller.sort_order
        uis = UserInquiry.objects.filter(assigned_to__isnull=True)
        ui_callers = Caller.objects.filter(sort_order__gt=last_ui_caller_order).order_by(
            'sort_order') | Caller.objects.filter(sort_order__lte=last_ui_caller_order).order_by('sort_order')
        if not uis:
            logger.info("No user inquiries to assign caller to")
        prev_caller = None
        for ui, caller in itertools.izip(uis, itertools.cycle(ui_callers)):
            try:
                ui.assigned_to = caller.user
                ui.save()
                if prev_caller:
                    prev_caller.last_call_inquiry = False
                    prev_caller.save()
                caller.last_call_inquiry = True
                caller.save()
                prev_caller = caller
            except:
                logger.exception("Script:: CALLER_ASSIGNMENT:: Error assigning caller for inquiry: %s", ui.id)
        logger.info("Script:: CALLER_ASSIGNMENT:: Script Ended at :%s", timezone.now())
