from __future__ import print_function
"""
    Schedule EOD tasks for all bookings.
"""

from django.conf import settings
from django.utils import timezone
from core.models.booking import BookingPackage, BookingPackagePanel, Booking, BookingExpectedEOD
from core.models.master import BookingOpsStatus, Workshop
from collections import OrderedDict
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc
from core.models.workshop import WorkshopStepsOfWork
import logging
logger = logging.getLogger(__name__)


BUMPER_WORKSHOP_RESOURCES = [{'name': 'Denter', 'count': 0},
           {'name': 'PainterHelper', 'count': 0},
           {'name': 'Painter', 'count': 0},
           {'name': 'Polisher', 'count': 0},
           {'name': 'Paintbooth', 'count': 1},
           {'name': 'WashingBay', 'count': 1},
           {'name': 'Batman', 'count': 10}
    ]


def build_resource_datewise(days_to_plan_for, num_of_working_hrs):
    today = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
    for item in BUMPER_WORKSHOP_RESOURCES:
        daily_avilable_hrs = {}
        for num in range(0, days_to_plan_for, 1):
            logger.info('SCHEDULING_EOD_WORKSHOP:: Building res for date ->%s' % str((today + timezone.timedelta(days=num)).date()))
            daily_avilable_hrs[str((today + timezone.timedelta(days=num)).date())] = {
                'total_minutes_available': num_of_working_hrs[str((today + timezone.timedelta(days=num)).date())] * item['count'] * 60,
                'minutes_remaining': num_of_working_hrs[str((today + timezone.timedelta(days=num)).date())] * item['count'] * 60,
            }
        item['hrs_mapping'] = daily_avilable_hrs


def get_panels_breakup(booking):
    """
        For now R = D1, S = D1, D2 = D1
    :param booking:
    :return:
    """
    breakup_of_panels = {
        'D1': 0,
        'D3': 0,
    }

    has_full_body = BookingPackage.objects.filter(booking_id=booking.id, package__package__category=3).exists()

    if has_full_body:
        breakup_of_panels = {
            'D1': 9,
            'D3': 1,
        }
    else:
        all_panels_in_booking = BookingPackagePanel.objects.select_related('panel')\
            .filter(booking_package__booking_id=booking.id, booking_package__package__package__category__in=[2,3],
                    panel__car_panel__part_type=1)

        for panel in all_panels_in_booking:
            if panel.panel.type_of_work in [5, 6, 7]:
                breakup_of_panels['D3'] += 1
            else:
                breakup_of_panels['D1'] += 1

    return breakup_of_panels


def get_days_spent_in_workshop(workshop_reached_time, end_date):
    start_date = workshop_reached_time
    if workshop_reached_time.hour > 15:
        start_date = workshop_reached_time + timezone.timedelta(days=1)

    # to accommodate 0 based days we get from difference
    num_of_working_days = 0
    while start_date.date() <= end_date.date():
        start_date = start_date + timezone.timedelta(days=1)
        if start_date.isoweekday() == 7:
            # to remove sunday from scheduling
            continue
        num_of_working_days += 1

    #num_of_working_days = ((end_date.date() - start_date.date()).days) + 1
    return num_of_working_days


def get_status_at_start_of_day(booking, date):
    start_of_day_time_utc = make_datetime_timezone_aware_convert_to_utc(str(date)+" 00:00:00", "+0530")

    logger.info("SCHEDULING_EOD_WORKSHOP:: get_status_at_start_of_day booking id=%s" % booking.id)
    logger.info("SCHEDULING_EOD_WORKSHOP:: get_status_at_start_of_day date to consider=%s" % date)
    logger.info("SCHEDULING_EOD_WORKSHOP:: get_status_at_start_of_day start of day utc=%s" % start_of_day_time_utc)
    logger.info("SCHEDULING_EOD_WORKSHOP:: get_status_at_start_of_day booking updated at=%s" % booking.updated_at)

    if booking.updated_at < start_of_day_time_utc:
        last_update_of_booking_before_today = booking
    else:
        last_status_booking = booking.history.filter(updated_at__lt=start_of_day_time_utc).order_by('updated_at').last()
        if last_status_booking:
            last_update_of_booking_before_today = last_status_booking
        else:
            logger.info("SCHEDULING_EOD_WORKSHOP:: get_status_at_start_of_day update after start of day + no history")
            last_update_of_booking_before_today = booking

    return {
        'last_status': last_update_of_booking_before_today.status.flow_order_num,
        'last_ops_status': last_update_of_booking_before_today.ops_status.flow_order_num if last_update_of_booking_before_today.ops_status else None,
    }


def get_resource_availablity_for_date(resource_type, num_of_hrs_required, date_to_consider):
    for item in BUMPER_WORKSHOP_RESOURCES:
        if item['name'] == resource_type:
            if str(date_to_consider.date()) in item['hrs_mapping'] \
                    and item['hrs_mapping'][str(date_to_consider.date())]['minutes_remaining'] > 0 \
                    and item['hrs_mapping'][str(date_to_consider.date())]['minutes_remaining'] > num_of_hrs_required:
                return True

    return False


def reduce_resources_from_date(date_to_consider, resource_consumption):
    for res in resource_consumption:
        # proceed only if resource is consumed.
        if resource_consumption[res] > 0:
            for item in BUMPER_WORKSHOP_RESOURCES:
                if item['name'] == res:
                    item['hrs_mapping'][str(date_to_consider.date())]['minutes_remaining'] = item['hrs_mapping'][str(date_to_consider.date())]['minutes_remaining'] - resource_consumption[res]


def process_step(seq_item, panels_breakup, date_to_process):
    # TODO: time are at per resource level, if multiple resource work in parallel then time should be split.
    # but for now taking in account only complete task so not needed.
    total_time_used_for_step = {
        'Denter': 0,
        'PainterHelper': 0,
        'Painter': 0,
        'Polisher': 0,
        'Paintbooth': 0,
        'WashingBay': 0,
        'Batman': 0,
    }

    res_required = ''

    total_time_required_at_this_task = 0
    max_car_level_time = 0
    for type_of_panel in panels_breakup:
        # get details of the task using seq number
        task = WorkshopStepsOfWork.objects.filter(ops_status__flow_order_num=seq_item['seq'],
                                                  type_of_damage=type_of_panel).first()

        if not task:
            raise Exception('No matching task for this seq =%s, type_of_panel=%s' % (seq_item, type_of_panel))

        if not res_required:
            res_required = task.resources_used

        if 'effort' in seq_item:
            sub_task = WorkshopStepsOfWork.objects.filter(
                ops_status__flow_order_num=seq_item['effort']['seq_to_consider'], type_of_damage=type_of_panel).first()

            car_level_time = sub_task.processing_time_car_level * seq_item['effort']['portion']
            if car_level_time > max_car_level_time:
                max_car_level_time = car_level_time
            panel_level_time = sub_task.processing_time_panel_level * panels_breakup[type_of_panel] * seq_item['effort']['portion']
        else:
            car_level_time = task.processing_time_car_level
            if car_level_time > max_car_level_time:
                max_car_level_time = car_level_time
            panel_level_time = task.processing_time_panel_level * panels_breakup[type_of_panel]

        total_time_required_at_this_task += panel_level_time

    total_time_required_at_this_task += max_car_level_time

    # TODO: enhancement, for now Diff between D1 and D3 is only of time effort and not resource. this can change later.
    # But not required as of now.

    are_resources_left_for_this_step = True

    task_resources_required_both = str(res_required).split('&')
    for task_resources_required_optional in task_resources_required_both:
        task_resources_required = str(task_resources_required_optional).split('|')

        alt_resource_left = False
        for alt_resource in task_resources_required:
            if alt_resource == 'Painter':
                pass
            if get_resource_availablity_for_date(alt_resource, total_time_required_at_this_task, date_to_process):
                alt_resource_left = True
                total_time_used_for_step[alt_resource] = total_time_required_at_this_task
                break

        if not alt_resource_left:
            # looked for all possible person that could do this work. but none have time so it cannot be done today.
            are_resources_left_for_this_step = False
            break

    return are_resources_left_for_this_step, total_time_used_for_step, total_time_required_at_this_task

# execution plan as per SLA.
# day: seq of work
# day: {'seq': seq of work_at_eod, 'effort': {'seq_to_consider': seq_to_consider_cal_overall_work, 'portion': 0.5}}
EXECUTION_PLANS = {
    'D1_3_D3_0': {
        1: [{'seq': 311}, {'seq': 312}, {'seq': 313}, {'seq': 314}, {'seq': 315}],
        2: [{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}, {'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        3: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'D1_2_D3_1': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        2: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}, {'seq': 314}, {'seq': 315}],
        3: [{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}],
        4: [{'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        5: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'D1_1_D3_2': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.25}}],
        2: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.25}}],
        3: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.25}}],
        4: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.25}}, {'seq': 314}, {'seq': 315},{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}],
        5: [{'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        6: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'D1_6_D3_0': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        2: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}, {'seq': 314}, {'seq': 315}],
        3: [{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}, {'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        4: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'D1_5_D3_1': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.33}}],
        2: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.33}}],
        3: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.33}},{'seq': 314}, {'seq': 315}],
        4: [{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}],
        5: [{'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        6: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'D1_4_D3_2': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        2: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        3: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        4: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.5}},{'seq': 314}, {'seq': 315},],
        5: [{'seq': 316}, {'seq': 317}],
        6: [{'seq': 318}, {'seq': 319}, {'seq': 320}, {'seq': 321}, {'seq': 322}, {'seq': 323}],
        7: [{'seq': 324}, {'seq': 325}, {'seq': 326}, {'seq': 327}, {'seq': 328}],
    },
    'Panels_GT_6': {
        1: [{'seq': 311}, {'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        2: [{'seq': 312, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        3: [{'seq': 313, 'effort': {'seq_to_consider': 313, 'portion': 0.5}}],
        4: [{'seq': 314}, {'seq': 315}],
        5: [{'seq': 316}, {'seq': 317}, {'seq': 318}, {'seq': 319}],
        6: [{'seq': 320}],
        7: [{'seq': 321}, {'seq': 322}, {'seq': 323}],
        8: [{'seq': 324}],
        9: [{'seq': 325}, {'seq': 326}],
        10: [{'seq': 327}, {'seq': 328}],
    }
}


def get_expected_end_of_day(booking_id, workshop_reached_time, date_to_process, panels_breakup, status_at_start_of_day,
                            working_hrs_available):
    execution_plan = {}
    # need case for when d1 = 0 and D3 < 3

    if (panels_breakup['D1'] + panels_breakup['D3']) >= 7 or (panels_breakup['D3'] >= 4):
        execution_plan = EXECUTION_PLANS['Panels_GT_6']

    elif panels_breakup['D1'] in [1, 2, 3] and panels_breakup['D3'] == 0:
        execution_plan = EXECUTION_PLANS['D1_3_D3_0']

    elif (panels_breakup['D1'] in [1, 2] and panels_breakup['D3'] == 1) or (panels_breakup['D1'] == 0 and panels_breakup['D3'] == 1):
        execution_plan = EXECUTION_PLANS['D1_2_D3_1']

    elif (panels_breakup['D1'] == 1 and panels_breakup['D3'] == 2) or (panels_breakup['D1'] == 0 and panels_breakup['D3'] == 3) or (panels_breakup['D1'] == 0 and panels_breakup['D3'] == 2):
        execution_plan = EXECUTION_PLANS['D1_1_D3_2']

    elif panels_breakup['D1'] in [4, 5, 6] and panels_breakup['D3'] == 0:
        execution_plan = EXECUTION_PLANS['D1_6_D3_0']

    elif (panels_breakup['D1'] in [4, 5] and panels_breakup['D3'] == 1) or (panels_breakup['D1'] == 3 and panels_breakup['D3'] == 1):
        execution_plan = EXECUTION_PLANS['D1_5_D3_1']

    elif (panels_breakup['D1'] >= 3 and panels_breakup['D3'] >= 1) and (panels_breakup['D1'] + panels_breakup['D3'] <= 6):
        execution_plan = EXECUTION_PLANS['D1_4_D3_2']

    if not execution_plan:
        raise Exception('!!!!!!!  Booking %s does not fit in any execution plan, panels: %s !!!!!!' % (booking_id, panels_breakup))

    days_in_workshop = get_days_spent_in_workshop(workshop_reached_time, date_to_process)
    execution_plan_for_selected_day = {}
    if days_in_workshop < 0:
        #  i.e work on booking is going to start tomorrow.
        execution_plan_for_selected_day = {'tasks': [{'seq': 311}], 'delay_in_days': 0}
    elif days_in_workshop in execution_plan:
        #  i.e booking has not exceeded the max allocated time.
        execution_plan_for_selected_day = {'tasks': execution_plan[days_in_workshop], 'delay_in_days': 0}
    else:
        #  find the last day in execution plan eg. 4th day.
        last_day = 0
        for item in execution_plan:
            if item > last_day:
                last_day = item

        execution_plan_for_selected_day = {'tasks': execution_plan[last_day], 'delay_in_days': last_day - days_in_workshop}

    ops_status_at_start = status_at_start_of_day['last_ops_status']

    if not ops_status_at_start:
        ops_status_at_start = 311

    # get first task for selected date
    first_task_for_selected_date = execution_plan_for_selected_day['tasks'][0]
    seq_list_to_process = []
    if 'effort' not in first_task_for_selected_date:
        # no continued task.
        # get the list of tasks that needs to be done and filter based on min and max status.
        for item in execution_plan:
            if item <= days_in_workshop:
                for task in execution_plan[item]:
                    if task['seq'] > ops_status_at_start and task['seq'] <= \
                            execution_plan_for_selected_day['tasks'][-1]['seq']:
                        seq_list_to_process.append(task)
            else:
                break
    else:
        if first_task_for_selected_date['seq'] == ops_status_at_start:
            # since it is partial task. We will assume that last tasks are complete. and start doing all tasks for today.
            for task in execution_plan_for_selected_day['tasks']:
                seq_list_to_process.append(task)

        elif first_task_for_selected_date['seq'] > ops_status_at_start:
            # get the list of tasks that needs to be done and filter based on min and max status.
            for item in execution_plan:
                if item <= days_in_workshop:
                    for task in execution_plan[item]:
                        if task['seq'] > ops_status_at_start and task['seq'] <= execution_plan_for_selected_day['tasks'][-1]['seq']:
                            seq_list_to_process.append(task)
                else:
                    break

        elif first_task_for_selected_date['seq'] < ops_status_at_start:
            # if partial task is already completed.
            for task in execution_plan_for_selected_day['tasks']:
                if task['seq'] > ops_status_at_start:
                    seq_list_to_process.append(task)

    total_time_used_for_date = {
        'Denter': 0,
        'PainterHelper': 0,
        'Painter': 0,
        'Polisher': 0,
        'Paintbooth': 0,
        'WashingBay': 0,
        'Batman': 0,
    }
    total_hr_worked_on_booking_for_date = 0
    new_ops_status_reached = ops_status_at_start

    tasks_done_for_date = []
    for seq_item in seq_list_to_process:
        are_resources_left_for_this_step, \
        total_time_used_for_step, \
        total_time_required_at_this_task = process_step(seq_item, panels_breakup, date_to_process)

        total_hr_worked_on_booking_for_date += total_time_required_at_this_task
        if total_hr_worked_on_booking_for_date > (working_hrs_available*60):
            # max work that can be done on car is 9 hours.
            break

        if are_resources_left_for_this_step:
            # update the last_status for this task to be this.
            new_ops_status_reached = seq_item['seq']
            # schedule this task for given date as resources there.
            for item in BUMPER_WORKSHOP_RESOURCES:
                if item['name'] in total_time_used_for_step:
                    total_time_used_for_date[item['name']] += total_time_used_for_step[item['name']]

            reduce_resources_from_date(date_to_process, total_time_used_for_step)
            tasks_done_for_date.append({
                "seq_num": seq_item['seq'],
                "seq": get_ops_desc_from_seq(seq_item['seq']),
                "time": total_time_required_at_this_task
            })
        else:
            # break the loops and exit for the day as no resources for this day
            # and no further task can be done.
            break

    return {
        'eod_task_seq': execution_plan_for_selected_day['tasks'][-1]['seq'],
        'status_at_end_of_day': {'last_ops_status': new_ops_status_reached},
        'total_time_used_for_date': total_time_used_for_date,
        'delay': new_ops_status_reached < execution_plan_for_selected_day['tasks'][-1]['seq'],
        'days_in_workshop': days_in_workshop,
        'tasks_done_for_date': tasks_done_for_date,
    }


def get_ops_desc_from_seq(seq):
    ops_status = BookingOpsStatus.objects.filter(flow_order_num=seq).first()
    return ops_status.ops_status_desc


def generate_workshop_schedule(days_to_plan_for, avail_resources, remove_list, workshop_id, use_current_status=True,
                               working_hrs_available=9):
    # TODO: Find delay from expected status.
    # TODO: when considering next day then priortize untouched.
    logger.info("SCHEDULING_EOD_WORKSHOP:: Script started - current_time: %s" % timezone.now())
    today = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
    try:
        for item in BUMPER_WORKSHOP_RESOURCES:
            if item["name"] in avail_resources:
                item["count"] = int(avail_resources[item["name"]])

        datewise_booking_allocation = {}
        datewise_available_working_hrs = {}
        for num in range(0, days_to_plan_for, 1):
            dt_to_consider = today + timezone.timedelta(days=num)
            datewise_booking_allocation[str(dt_to_consider.date())] = []
            datewise_available_working_hrs[
                str(dt_to_consider.date())] = working_hrs_available
            if use_current_status and num == 0:
                if dt_to_consider.hour >= 19:
                    datewise_available_working_hrs[str(dt_to_consider.date())] = 0
                elif dt_to_consider.hour < 10:
                    datewise_available_working_hrs[str(dt_to_consider.date())] = working_hrs_available
                else:
                    datewise_available_working_hrs[str(dt_to_consider.date())] = 19 - dt_to_consider.hour


        build_resource_datewise(days_to_plan_for, datewise_available_working_hrs)

        # Get all panels in all bookings for which work needs to be done,
        # and that are in workshop in ready to work status.
        workshop_ids_to_consider = [workshop_id]
        if workshop_id == 17:
            workshop_ids_to_consider = [16, 17, 18]
        all_bookings_in_workshop = Booking.objects.filter(status__in=[12, 13],
                                                          estimate_complete_time__isnull=False,
                                                          rework_booking_id__isnull=True,
                                                          workshop_id__in=workshop_ids_to_consider).order_by('workshop_eta')
        if remove_list:
            all_bookings_in_workshop.exclude(id__in=remove_list)

        all_bookings_with_eod = []
        projected_delayed_bookings = set()

        for booking in all_bookings_in_workshop:
            has_dent_or_fbb = BookingPackage.objects.filter(booking_id=booking.id, package__package__category__in=[2, 3]).exists()
            if has_dent_or_fbb:
                workshop_reached_time = _convert_to_given_timezone(booking.workshop_reached_time, settings.TIME_ZONE)
                customer_eta = _convert_to_given_timezone(booking.estimate_complete_time, settings.TIME_ZONE)
                workshop_eta = _convert_to_given_timezone(booking.workshop_eta, settings.TIME_ZONE)
                panels_breakup = get_panels_breakup(booking)
                workshop_vendor = booking.workshop.name

                work_to_done_in_day_datewise = {}
                date_to_process = today
                for num in range(0, days_to_plan_for, 1):
                    date_to_process = today + timezone.timedelta(days=num)

                    if date_to_process.isoweekday() == 7:
                        # to remove sunday from scheduling
                        continue

                    if date_to_process == today:
                        # taking status at start of day as, output need resource allocation for complete day.
                        # if current status is taken then full resource time will be available but that is not the
                        # case in realty.
                        if not use_current_status:
                            status_at_start_of_day = get_status_at_start_of_day(booking, today.date())
                        else:
                            booking_expected_eod = BookingExpectedEOD.objects\
                                .filter(booking=booking,for_date=today.date())\
                                .order_by('-created_at').first()

                            if booking_expected_eod:
                                status_at_start_of_day = {
                                    'last_status': booking_expected_eod.status.flow_order_num,
                                    'last_ops_status': booking_expected_eod.ops_status.flow_order_num if booking_expected_eod.ops_status else None,
                                }
                            else:
                                status_at_start_of_day = {
                                    'last_status': booking.status.flow_order_num,
                                    'last_ops_status': booking.ops_status.flow_order_num if booking.ops_status else None,
                                }
                    else:
                        if date_to_process.isoweekday() == 1:
                            if str((date_to_process - timezone.timedelta(
                                    days=2)).date()) not in work_to_done_in_day_datewise:
                                status_at_start_of_day = get_status_at_start_of_day(booking, date_to_process.date())
                            else:
                                status_at_start_of_day = \
                                work_to_done_in_day_datewise[str((date_to_process - timezone.timedelta(days=2)).date())][
                                    'status_at_end_of_day']
                        else:
                            if str((date_to_process - timezone.timedelta(
                                    days=1)).date()) not in work_to_done_in_day_datewise:
                                status_at_start_of_day = get_status_at_start_of_day(booking, date_to_process.date())
                            else:
                                status_at_start_of_day = \
                                work_to_done_in_day_datewise[str((date_to_process - timezone.timedelta(days=1)).date())][
                                    'status_at_end_of_day']

                    expected_end_of_day = get_expected_end_of_day(booking.id, workshop_reached_time,
                                                                  date_to_process, panels_breakup,
                                                                  status_at_start_of_day, working_hrs_available)
                    if expected_end_of_day['delay']:
                        projected_delayed_bookings.add("%s_%s" % (booking.id, workshop_vendor))

                    data = {
                        'expected_status_as_per_sla': get_ops_desc_from_seq(expected_end_of_day['eod_task_seq']),
                        'status_at_start_of_day': status_at_start_of_day,
                        'status_at_end_of_day': expected_end_of_day['status_at_end_of_day'],
                        'total_time_used_for_date': expected_end_of_day['total_time_used_for_date'],
                        'delay': expected_end_of_day['delay'],
                        'days_in_workshop': expected_end_of_day['days_in_workshop'],
                        'tasks_done_for_date': expected_end_of_day['tasks_done_for_date'],
                    }
                    total_hrs_used = 0
                    if expected_end_of_day['total_time_used_for_date']:
                        for work_data in expected_end_of_day['total_time_used_for_date'].iteritems():
                            total_hrs_used += work_data[1]

                        if total_hrs_used > 0:
                            formatted_data = data
                            formatted_data["booking_id"] = booking.id
                            formatted_data["car_model"] = booking.usercar.car_model.name
                            formatted_data["car_reg_num"] = booking.usercar.registration_number
                            formatted_data["workshop"] = booking.workshop.name
                            formatted_data["panels_breakup"] = panels_breakup
                            formatted_data["workshop_eta"] = workshop_eta
                            formatted_data["customer_eta"] = customer_eta
                            formatted_data["current_status"] = booking.ops_status.ops_status_desc if booking.ops_status else ""
                            formatted_data["status_at_start_of_day_desc"] = get_ops_desc_from_seq(data['status_at_start_of_day']['last_ops_status']) if data['status_at_start_of_day']['last_ops_status'] else "Not Started"
                            formatted_data["status_at_end_of_day_desc"] = get_ops_desc_from_seq(data['status_at_end_of_day']['last_ops_status'])
                            datewise_booking_allocation[str(date_to_process.date())].append(formatted_data)

                    work_to_done_in_day_datewise[str(date_to_process.date())] = data

                ordered_work_to_done_in_day_datewise = OrderedDict(sorted(work_to_done_in_day_datewise.items(), key=lambda t: t[0]))

                cannot_meet_workshop_eta = False
                if len(ordered_work_to_done_in_day_datewise.values()) > 0:
                    last_data = ordered_work_to_done_in_day_datewise.values()[-1]
                    if workshop_eta.date() > date_to_process.date() and last_data['status_at_end_of_day']['last_ops_status'] < 327:
                        cannot_meet_workshop_eta = True

                booking_detail = {
                    'booking_id': booking.id,
                    'workshop_vendor': workshop_vendor,
                    'workshop_id': booking.workshop.id,
                    'workshop_reached_time': workshop_reached_time,
                    'workshop_eta': workshop_eta,
                    'customer_eta': customer_eta,
                    'work_to_done_in_day_datewise': ordered_work_to_done_in_day_datewise,
                    'panels_breakup': panels_breakup,
                    'cannot_meet_workshop_eta': cannot_meet_workshop_eta
                    # 'is_untouched': is_untouched,
                }
                all_bookings_with_eod.append(booking_detail)

        for item in BUMPER_WORKSHOP_RESOURCES:
            ordered_datewise = OrderedDict(sorted(item['hrs_mapping'].items(), key=lambda t: t[0]))
            item['hrs_mapping'] = ordered_datewise

        return all_bookings_with_eod, projected_delayed_bookings, BUMPER_WORKSHOP_RESOURCES,datewise_booking_allocation
    except:
        logger.exception('Failed to create EOD list')
