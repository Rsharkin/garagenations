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
from core.managers.workshopManager import generate_workshop_schedule
import logging
logger = logging.getLogger('bumper.scripts')

# Config
bumper_resources = [
    {'name': 'Denter', 'count': 2},
    {'name': 'PainterHelper', 'count': 2},
    {'name': 'Painter', 'count': 2},
    {'name': 'Polisher', 'count': 1},
    {'name': 'Paintbooth', 'count': 1},
    {'name': 'Batman', 'count': 5},
]

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


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: SCHEDULING_WORKSHOP_OPTIMIZER:: Schedule task in workshop'

    def handle(self, *args, **options):
        try:
            avail_resources = {
                'Denter': 4,
                'Painter': 5,
                'PainterHelper': 3,
                'Polisher': 2,
            }
            all_bookings_with_eod, \
            projected_delayed_bookings, \
            bumper_workshop_resources, \
            datewise_booking_allocation = generate_workshop_schedule(7, avail_resources, [], 17, use_current_status=False,
                               working_hrs_available=9)

            all_booking_all_tasks = []

            for date in datewise_booking_allocation:
                data = datewise_booking_allocation[date]

                all_booking_all_tasks.append({
                    'id': data.booking_id,
                    'tasks': data.tasks_done_for_date
                })

            logger.info("Script:: SCHEDULING_WORKSHOP_OPTIMIZER:: Bookings & their tasks To Process: %s" % all_booking_all_tasks)

            bumper_horizon = 0
            for booking in all_booking_all_tasks:
                for task in booking['tasks']:
                    bumper_horizon += task['processing_time']

            logger.info("Script:: SCHEDULING_WORKSHOP_OPTIMIZER::%s" % bumper_horizon)

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
            logger.exception("Script:: SCHEDULING_WORKSHOP_OPTIMIZER:: Failed to process to bookings")