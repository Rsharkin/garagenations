from __future__ import print_function
"""
    Schedule tasks in workshop using Google ORtools
"""

# Import Python wrapper for or-tools constraint solver.
from ortools.constraint_solver import pywrapcp
import time, os, copy, collections
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.booking import BookingPackagePanel, Booking
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc\
    , format_datetime_for_grid
import logging
logger = logging.getLogger('bumper.scripts')

# Config
PANELS_GROUP_SIZE = 3
bumper_resources = [
    {'name': 'Denter', 'count': 2},
    {'name': 'PainterHelper', 'count': 2},
    {'name': 'Painter', 'count': 2},
    {'name': 'Polisher', 'count': 1},
    {'name': 'Paintbooth', 'count': 1},
    {'name': 'Batman', 'count': 5},
]

ALL_STEPS = [
    {'name': 'denting', 'resource_type_req': 'Denter', 'seq': 1},
    {'name': 'remove_refit', 'resource_type_req': 'Denter', 'seq': 2},
    {'name': 'bf_apply', 'resource_type_req': 'Denter', 'seq': 3},
    {'name': 'bf_sanding', 'resource_type_req': 'Denter', 'seq': 4},
    {'name': 'putty_apply', 'resource_type_req': 'Denter', 'seq': 5},
    {'name': 'putty_sanding', 'resource_type_req': 'Denter', 'seq': 6},
    {'name': 'primer_masking', 'resource_type_req': 'PainterHelper|Painter', 'seq': 7},
    {'name': 'primer_apply', 'resource_type_req': 'PainterHelper|Painter', 'seq': 8},
    {'name': 'primer_sanding', 'resource_type_req': 'PainterHelper|Painter', 'seq': 9},
    {'name': 'check_putty', 'resource_type_req': 'PainterHelper|Painter', 'seq': 10},
    {'name': 'check_putty_drying', 'resource_type_req': 'Batman', 'seq': 11},
    {'name': 'check_putty_sanding', 'resource_type_req': 'PainterHelper|Painter', 'seq': 12},
    {'name': 'washing', 'resource_type_req': 'PainterHelper|Painter', 'seq': 13},
    {'name': 'paint_masking', 'resource_type_req': 'PainterHelper|Painter', 'seq': 14},
    {'name': 'painting', 'resource_type_req': 'Painter&Paintbooth', 'seq': 15},
    {'name': 'baking', 'resource_type_req': 'Paintbooth', 'seq': 16},
    {'name': 'polishing', 'resource_type_req': 'Polisher', 'seq': 17},
    {'name': 'part_fitting', 'resource_type_req': 'Denter', 'seq': 18},
]

CHECKPOINTS = [
    {'step': ALL_STEPS[12], 'level': 'booking', 'processing_time': 30},
    {'step': ALL_STEPS[14], 'level': 'panel', 'processing_time': {2: 10, 1: 5, 3: 10}},
]

STEPS_OF_WORK_PER_PANEL = [
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[0], 'processing_time': 20},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[2], 'processing_time': 10},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[3], 'processing_time': 15},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[4], 'processing_time': 10},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[5], 'processing_time': 15},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[6], 'processing_time': 30},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[7], 'processing_time': 20},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[8], 'processing_time': 30},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[9], 'processing_time': 10},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[10], 'processing_time': 10},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[11], 'processing_time': 5},
    # {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[12], 'processing_time': 30},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[13], 'processing_time': 45},
    # {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[14], 'processing_time': 35},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[15], 'processing_time': 30},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[16], 'processing_time': 30},
    {'applicable_in_type_of_work': 2, 'step': ALL_STEPS[17], 'processing_time': 10},

    {'applicable_in_type_of_work': 3, 'step': ALL_STEPS[1], 'processing_time': 10},
]

TYPE_OF_WORK_SCRATCH = 1
TYPE_OF_WORK_DENT = 2
TYPE_OF_WORK_REPLACE = 3
TYPE_OF_WORK_PAINT_ONLY = 4
TYPE_OF_WORK_CRUMPLED_PANEL = 5
TYPE_OF_WORK_RUSTED_PANEL = 6
TYPE_OF_WORK_TEAR = 7
TYPE_OF_WORK_CLEANING = 8
TYPE_OF_WORK_REPLACE_FBB = 9

TYPE_OF_WORKS = (
    (TYPE_OF_WORK_SCRATCH, "Remove Scratches"),
    (TYPE_OF_WORK_DENT, "Remove Dents and Scratches"),
    (TYPE_OF_WORK_REPLACE, "Replace"),
    (TYPE_OF_WORK_PAINT_ONLY, "Paint Only"),
    (TYPE_OF_WORK_CRUMPLED_PANEL, "Crumpled panel"),
    (TYPE_OF_WORK_RUSTED_PANEL, "Rusted Panel"),
    (TYPE_OF_WORK_TEAR, "Tear"),
    (TYPE_OF_WORK_CLEANING, "Cleaning"),
    (TYPE_OF_WORK_REPLACE_FBB, "Replace"),
)


def get_steps_by_type_of_work(type_of_work):
    steps_to_do = []
    for item in STEPS_OF_WORK_PER_PANEL:
        if type_of_work == item['applicable_in_type_of_work']:
            steps_to_do.append(item)
    return steps_to_do


def get_checkpoint_steps(booking):
    all_panels_in_booking = BookingPackagePanel.objects.select_related('panel')\
        .filter(booking_package__booking_id=booking.id)

    all_types = {
    }
    for panel in all_panels_in_booking:
        if panel.panel.type_of_work in all_types:
            all_types[panel.panel.type_of_work] = all_types[panel.panel.type_of_work] + 1
        else:
            all_types[panel.panel.type_of_work] = 1

    all_steps = []
    for item in CHECKPOINTS:
        processing_time = 0
        if item['level'] == 'booking':
            processing_time = item['processing_time']
        elif item['level'] == 'panel':
            for type_of_panel in all_types:
                if type_of_panel in item['processing_time']:
                    processing_time += item['processing_time'][type_of_panel] * all_types[type_of_panel]

        all_steps.append({'step': item['step'], 'processing_time': processing_time})
    return all_steps


def get_resource_seq_by_type(resource_type):
    matching_resources = []
    for r in bumper_resources:
        i = 1
        while i <= r['count']:
            if resource_type == r['name']:
                resource_name = "%s%i" % (r['name'], i)
                matching_resources.append(resource_name)
            i += 1

    return matching_resources


def get_groups_of_work_from_booking(booking):
    """
        make groups of panels in booking by type of work. Max size of group is defined.
    :param booking:
    :return:
    """
    all_panels_in_booking = BookingPackagePanel.objects.select_related('panel')\
        .filter(booking_package__booking_id=booking.id)

    all_groups = {
        #2: [{'name':'fender_right_bumper_front', 'units': 2}]
    }
    for panel in all_panels_in_booking:
        if panel.panel.type_of_work in all_groups:
            # groups for this type of work exists, find group that have space left.
            groups_by_type_of_work = all_groups[panel.panel.type_of_work]
            panel_added = False
            for group in groups_by_type_of_work:
                # check against panels_in_group_limit if panel can be added here else create a new group.
                if group['units'] < PANELS_GROUP_SIZE:
                    group['name'] = "%s,%s" % (group['name'], str(panel.panel.car_panel.name).replace(' ','_'))
                    group['units'] += 1
                    panel_added = True

            if not panel_added:
                groups_by_type_of_work.append({'name': str(panel.panel.car_panel.name).replace(' ','_'), 'units': 1})
        else:
            all_groups[panel.panel.type_of_work] = [{'name': str(panel.panel.car_panel.name).replace(' ','_'), 'units': 1}]

    return all_groups


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: SCHEDULING_WORKSHOP:: Schedule task in workshop'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: SCHEDULING_WORKSHOP:: Script started - current_time: %s" % current_time)

        # pickup time in next day
        current_context_time = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
        date_for_tomorrow_in_current_context = current_context_time + timezone.timedelta(days=1)
        start_time = make_datetime_timezone_aware_convert_to_utc(str(date_for_tomorrow_in_current_context.date())+" 00:00:00", "+0530")
        end_time = start_time + timezone.timedelta(hours=24)

        logger.info("Script:: SCHEDULING_WORKSHOP:: Tomorrow's start_time: %s - end_Time: %s" % (start_time, end_time))

        try:
            # Get all panels in all bookings for which work needs to be done,
            # and that are in workshop in ready to work status.
            all_bookings_in_workshop = Booking.objects.filter(status__in=[12,13])
            all_booking_all_tasks = []

            for booking in all_bookings_in_workshop:
                groups_of_work = get_groups_of_work_from_booking(booking)

                # all_panels_in_booking = BookingPackagePanel.objects.select_related('panel') \
                #     .filter(booking_package__booking_id=booking.id)

                booking_tasks_remaining = []
                groups = []
                for type_of_group in groups_of_work:
                    work_list = get_steps_by_type_of_work(type_of_group)
                    for group in groups_of_work[type_of_group]:
                        if group["name"] not in groups:
                            groups.append(group["name"])

                        for work in work_list:
                            booking_tasks_remaining.append({
                                'task_name': "Task(%s:%s)::%s::seq-%s" % (booking.id, group['name'], work['step']['name'],work['step']['seq']),  # (12435:fender_right)::denting::seq-1
                                'group_name': group['name'],
                                'type_of_work': work['step']['name'],
                                'resource': work['step']['resource_type_req'],
                                'processing_time': (work['processing_time'] * group['units']),
                                'seq': work['step']['seq'],
                            })

                checkpoint_tasks = []
                checkpoints = get_checkpoint_steps(booking)
                for checkpoint_num, checkpoint in enumerate(checkpoints):
                    if "Full_Car" not in groups:
                        groups.append("Full_Car")

                    t = {
                        'task_name': "Task(%s:Full_Car)::%s::seq-%s" % (booking.id, checkpoint['step']['name'], checkpoint['step']['seq']),
                        'group_name': "full_car",
                        'type_of_work': checkpoint['step']['name'],
                        'resource': checkpoint['step']['resource_type_req'],
                        'processing_time': checkpoint['processing_time'],
                        'seq': checkpoint['step']['seq'],
                    }
                    booking_tasks_remaining.append(t)
                    checkpoint_tasks.append(t)

                all_booking_all_tasks.append({
                    'id': booking.id,
                    'groups': groups,
                    'tasks': booking_tasks_remaining,
                    'checkpoints': checkpoint_tasks,
                })

            logger.info("Script:: SCHEDULING_WORKSHOP:: Bookings & their tasks To Process: %s" % all_booking_all_tasks)

            bumper_horizon = 0
            for booking in all_booking_all_tasks:
                for task in booking['tasks']:
                    bumper_horizon += task['processing_time']

            logger.info("Script:: SCHEDULING_WORKSHOP::%s" % bumper_horizon)

            task_to_interval = collections.OrderedDict()
            resource_to_intervals = {}
            all_resource_list = []

            for r in bumper_resources:
                i = 1
                while i <= r['count']:
                    resource_name = "%s%i" % (r['name'], i)
                    all_resource_list.append(resource_name)
                    resource_to_intervals[resource_name] = list()
                    i += 1

            # Create the solver.
            solver = pywrapcp.Solver('bumper workshop')

            # Create all interval based tasks for all bookings.
            for booking in all_booking_all_tasks:
                for task in booking['tasks']:
                    solver_task = solver.FixedDurationIntervalVar(0, bumper_horizon - task['processing_time'],
                                                                  task['processing_time'], False, task["task_name"])

                    task_to_interval[task['task_name']] = solver_task

                    # process multiple resource on same task
                    task_resources_required_both = str(task['resource']).split('&')

                    for req_resource_type in task_resources_required_both:
                        # process optional resources on same task
                        task_resources_required = str(req_resource_type).split('|')
                        RA_tasks_optional = list()
                        for resource_type in task_resources_required:
                            for resource_name in get_resource_seq_by_type(resource_type):
                                # Adding optional tasks
                                I_ = solver.FixedDurationIntervalVar(0, bumper_horizon - task['processing_time'],
                                                                     task['processing_time'],
                                                                     True, '%s_%s' % (task['task_name'], resource_name))

                                resource_to_intervals[resource_name].append(I_)
                                RA_tasks_optional.append(I_)
                                solver.Add(solver_task.StaysInSync(I_))

                        # one resource needs to get selected
                        solver.Add(solver.Sum([I_.PerformedExpr() for I_ in RA_tasks_optional]) == 1)

            # resources
            sequences = collections.OrderedDict()
            for R in all_resource_list:
                disj = solver.DisjunctiveConstraint(resource_to_intervals[R], R)
                sequences[R] = disj.SequenceVar()
                solver.Add(disj)

            # Precedences inside a job.
            # for booking in all_bookings_in_workshop:
            #     groups_of_work = get_groups_of_work_from_booking(booking)
            #     for type_of_group in groups_of_work:
            #         work_list = get_steps_by_type_of_work(type_of_group)
            #         for idx, group in enumerate(groups_of_work[type_of_group]):
            #             for task_num, work in enumerate( work_list):
            #                 # Do this using SEQ num rather than list index.
            #                 if task_num == len(work_list) - 1:
            #                     continue
            #                 solver.Add(task_to_interval["%s-%s-%s" % (booking.id, idx, task_num + 1)].StartsAfterEnd(
            #                     task_to_interval["%s-%s-%s" % (booking.id, idx, task_num)]))

            for booking in all_booking_all_tasks:
                # set precedence within booking tasks
                for group in booking['groups']:
                    # set precedence within group of works
                    all_task_within_group = [ item for item in booking["tasks"] if str(item["task_name"]).split("::")[0] == 'Task(%s:%s)'% (booking["id"], group)]
                    # is there a task with greater seq num than this task in this group
                    foo = sorted(all_task_within_group, key=lambda x: x['seq'])
                    max_task_to_process = len(foo) - 1
                    for idx, task in enumerate(foo):
                        if idx == max_task_to_process:
                            continue
                        solver.Add(task_to_interval[foo[idx+1]["task_name"]].StartsAfterEnd(
                                            task_to_interval[task["task_name"]]))

                    if len(all_task_within_group) > 0 and group != "Full_Car":
                        # set precedence for checkpoints
                        for checkpoint_task in booking["checkpoints"]:
                            seq_num = checkpoint_task["seq"]
                            all_tasks_below_checkpoint = [item for item in all_task_within_group if item["seq"] < seq_num]
                            if len(all_tasks_below_checkpoint) > 0:
                                # going through all group to get last task before seq
                                last_task = all_tasks_below_checkpoint[-1]
                                solver.Add(task_to_interval[checkpoint_task["task_name"]].StartsAfterEnd(
                                    task_to_interval[last_task["task_name"]]))



            # Objective
            # obj_var = solver.Max([((task_to_interval["%s-%s-%s" % (booking['id'], task['group_num'], task['task_num'])].EndExpr()
            #                                )for task in booking["tasks"]) for booking in all_booking_all_tasks])

            # obj_var = solver.Max([task_to_interval[booking['tasks'][-1]['task_name']].EndExpr()
            #                       for booking in all_booking_all_tasks if len(booking['tasks']) > 0])

            #  Last item as per seq to be done as soon as possible.
            obj_var = solver.Max([task_to_interval[sorted(booking["tasks"], key=lambda x: x['seq'])[-1]['task_name']].EndExpr()
                                  for booking in all_booking_all_tasks if len(booking['tasks']) > 0])

            objective_monitor = solver.Minimize(obj_var, 1)

            # Creates search phases.
            vars_phase = solver.Phase([obj_var],
                                      solver.CHOOSE_FIRST_UNBOUND,
                                      solver.ASSIGN_MIN_VALUE)

            sequence_phase = solver.Phase(sequences.values(),
                                          solver.SEQUENCE_DEFAULT)

            main_phase = solver.Compose([sequence_phase, vars_phase])

            # Create the solution collector.
            collector = solver.LastSolutionCollector()

            # Add the interesting variables to the SolutionCollector.
            collector.Add(sequences.values())
            collector.AddObjective(obj_var)

            for R in all_resource_list:
                sequence = sequences[R];
                sequence_count = sequence.Size();
                for j in range(0, sequence_count):
                    t = sequence.Interval(j)
                    collector.Add(t.StartExpr().Var())
                    collector.Add(t.EndExpr().Var())
            # Solve the problem.
            disp_col_width = 10

            if solver.Solve(main_phase, [objective_monitor, collector]):
                print("\nOptimal Schedule Length:", collector.ObjectiveValue(0), "\n")
                sol_line = ""
                sol_line_tasks = ""
                print("Optimal Schedule", "\n")

                for R in all_resource_list:
                    seq = sequences[R]
                    sol_line += R + ": "
                    sol_line_tasks += R + ": "
                    sequence = collector.ForwardSequence(0, seq)
                    seq_size = len(sequence)

                    for j in range(0, seq_size):
                        t = seq.Interval(sequence[j]);
                        # Add spaces to output to align columns.
                        sol_line_tasks += t.Name() + " " * disp_col_width

                    for j in range(0, seq_size):
                        t = seq.Interval(sequence[j]);
                        sol_tmp = "[" + str(collector.Value(0, t.StartExpr().Var())) + ","
                        sol_tmp += str(collector.Value(0, t.EndExpr().Var())) + "] "
                        # Add spaces to output to align columns.
                        sol_line += sol_tmp + " " * disp_col_width

                    sol_line += "\n"
                    sol_line_tasks += "\n"

                print(sol_line_tasks)
                print("Time Intervals for Tasks\n")
                print(sol_line)
        except:
            logger.exception("Script:: SCHEDULING_WORKSHOP:: Failed to process to bookings")