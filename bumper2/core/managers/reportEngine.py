# Inderjeet 24 Nov 2015
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db import connection
from math import ceil
import ujson
import logging
from core.managers import reportManagerConstants

log = logging.getLogger()

def json_encode(data):
    encoder = DjangoJSONEncoder()
    return encoder.encode(data)

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class ReportEngine(object):
    """
        generic grid
    """
    def __init__(self, view_type, generate_plan_rows=False, no_json_encoding=False):
        self.view_type = view_type
        self.fields = []
        self.url = ''
        self.default_rows_in_page = 10
        self.params_for_sql = {}
        self.default_sort_col = ""
        self.default_sort_ord = "desc"
        self.master_sql_col_map = {}
        self.filter_fields_data = {}
        self.generate_plan_rows = generate_plan_rows
        self.no_json_encoding = no_json_encoding
        # hold dicts like {view_type:[field_name]}
        self.exceptional_where_clause_view_types_fields = {}
        self.store_query_in_session_for_revisit = False
        self.select_count_query_over_groups = False
        self.group_by_query = ''

    def get_caption(self):
        return ''

    def get_current_fields(self):
        return self.fields

    def get_json_without_paging(self, request):
        """
            Function to get grid data without any paging.
        :param request:
        :return:
        """
        grid_obj = {
            '_search': request.query_params.get('_search'),
            'filters': request.query_params.get('filters'),
            'sidx': request.query_params.get('sidx'),
            'sord': request.query_params.get('sord'),
            'searchField': request.query_params.get('searchField'),
            'searchOper': request.query_params.get('searchOper'),
            'searchString': request.query_params.get('searchString'),
            'user': request.user,
        }
        # build SELECT query
        query, select_count_query = self.build_select_query(grid_obj)

        # Build Where Query
        query += self.filter_items_sql(grid_obj, request)
        # Build group Query
        query += self.group_by_items_sql(grid_obj)
        # build Sort Query
        query += self.sort_items_sql(grid_obj)

        #log.info('Query for grid %s' % query)
        rows = []

        cur = connection.cursor()
        try:
            cur.execute(query, self.params_for_sql)
            if not self.generate_plan_rows:
                rows = dictfetchall(cur)
            else:
                rows = cur.fetchall()
            cur.close()
        except:
            log.exception("Failed to get values for jq grid")
            cur.close()

        final_result = {
            'rows': rows,
            }

        if not self.generate_plan_rows and not self.no_json_encoding:
            return json_encode(final_result)
        else:
            return final_result

    def get_json_with_paging(self, request):
        """
            over ride get_json to use python cursors instead of the models
        """
        grid_obj = {
            'page': request.query_params.get('page', 1),
            'rows': request.query_params.get('rows', self.default_rows_in_page),
            '_search': request.query_params.get('_search'),
            'filters': request.query_params.get('filters'),
            'sidx': request.query_params.get('sidx'),
            'sord': request.query_params.get('sord'),
            'searchField': request.query_params.get('searchField'),
            'searchOper': request.query_params.get('searchOper'),
            'searchString': request.query_params.get('searchString'),
        }
        query, select_count_query = self.build_select_query(grid_obj)

        filter_query = self.filter_items_sql(grid_obj, request)
        query += filter_query
        select_count_query += filter_query

        query += self.group_by_items_sql(grid_obj)
        select_count_query += self.group_by_items_sql(grid_obj)

        if self.select_count_query_over_groups:
            select_count_query = 'SELECT COUNT(*) FROM ( SELECT COUNT(*) ' + select_count_query + ') groups'

        query += self.sort_items_sql(grid_obj)

        page_start = int(grid_obj['page']) - 1
        start_row = page_start * int(grid_obj['rows'])
        limit_query = ' LIMIT ' + str(start_row) + ',' + str(grid_obj['rows'])
        query += limit_query

        #log.info('Query for grid %s' % query)
        num_rows = 0
        rows=[]

        cur = connection.cursor()
        try:
            cur.execute( select_count_query + '; ' + query, self.params_for_sql)
            num_rows = cur.fetchone()
            if cur.nextset():
                if not self.generate_plan_rows:
                    rows = dictfetchall(cur)
                else:
                    rows = cur.fetchall()
            cur.close()
        except:
            log.exception("Failed to get values for jq grid")
            cur.close()

        final_result = {
            'page': grid_obj.get('page'),
            'total': int(ceil(float(num_rows[0]) / int(grid_obj.get('rows')))),
            'rows': rows,
            'records': num_rows[0]
            }

        if not self.generate_plan_rows and not self.no_json_encoding:
            return json_encode(final_result)
        else:
            return final_result

    def build_select_query(self, grid_obj):
        return ""

    def get_filters(self, grid_obj):
        _search = grid_obj.get('_search')
        filters = None

        if _search == 'true':
            _filters = grid_obj.get('filters')
            if _filters:
                try:
                    filters = _filters and ujson.loads(_filters)
                except ValueError:
                    return None

            if filters is None or not len(filters):
                field = grid_obj.get('searchField')
                op = grid_obj.get('searchOper')
                data = grid_obj.get('searchString')

                if all([field, op, data]):
                    filters = {
                        'groupOp': 'AND',
                        'rules': [{ 'op': op, 'field': field, 'data': data }]
                    }
        return filters

    def exceptional_filters(self, field, data):
        """
            Function to be overridden in child class if requirement of spl query on a field
            1) register -- view_type along with field name for exceptional where_clause handling
            2) Put the if else and handle exceptional code here.
        """
        return ""

    def filter_items_sql(self, grid_obj, request):
        # TODO Fix: only eq and cn are working
        filter_map = {
            'ne': " {0} != '%({1})s' ",
            'bn': " {0} not like '{1}%' ",
            'en': " {0} not like '%{1}' ",
            'nc': " {0} not like '%{1}%' ",
            'ni': ('%(field)s__in', True),
            'iin': " {0} in %({1})s ", # integer in
            'niin': " ({0} not in %({1})s OR {0} is null) ", # not in
            'eq': " {0} = %({1})s ",
            # subquery equal to
            'seq': " {0} = %({1})s )",
            'bw': " {0} like '{1}%' ",
            'gt': " {0} > %({1})s ",
            'ge': " {0} >= %({1})s ",
            'lt': " {0} < %({1})s ",
            'le': " {0} <= %({1})s ",
            'ew': " {0} like '%{1}' ",
            'cn': " {0} like %({1})s ",
            'cns': " {0} like %({1})s )",
            'deq': " (DATE(CONVERT_TZ({0},'+00:00','+05:30')) >= %({1})s and  DATE(CONVERT_TZ({0},'+00:00','+05:30')) <= %({2})s )",
            'dteq': " (CONVERT_TZ({0},'+00:00','+05:30') >= %({1})s and  CONVERT_TZ({0},'+00:00','+05:30') <= %({2})s )",
            '2dteqor': " ( (CONVERT_TZ({0},'+00:00','+05:30') >= %({1})s and  CONVERT_TZ({0},'+00:00','+05:30') <= %({2})s ) OR  (CONVERT_TZ({3},'+00:00','+05:30') >= %({4})s and  CONVERT_TZ({3},'+00:00','+05:30') <= %({5})s ) )",
            '2deqor': " (date(CONVERT_TZ({0},'+00:00','+05:30')) = %({2})s OR  date(CONVERT_TZ({1},'+00:00','+05:30')) = %({2})s )",
            'dob': " DATE_ADD({0}, INTERVAL YEAR(CURDATE())-YEAR({0}) YEAR) BETWEEN DATE(%({1})s) AND DATE(%({2})s)", # for birthdays
            # Hard code query no parameter input
            'hc': "",
        }
        additional_where_sql = ''

        _filters = self.get_filters(grid_obj)
        _search = grid_obj.get('_search')

        if str(_search).upper() == 'TRUE':
            if _filters is None:
                return ''

            for rule in _filters['rules']:
                op, field, data = rule['op'], rule['field'], rule['data']
                self.filter_fields_data[str(field).replace(' ', '_')] = data
                if data == 0 or data == '0':
                    continue

                filter_fmt = filter_map[op]
                if 'like' in filter_fmt:
                    data = '%' + data + '%'

                if self.exceptional_where_clause_view_types_fields.get(self.view_type) \
                        and field in self.exceptional_where_clause_view_types_fields.get(self.view_type):
                    additional_where_sql += self.exceptional_filters(field, data)
                    continue

                if op == 'deq':
                    # operation for searching date range in grid
                    old_field = str(field).replace(' ', '_')
                    field = self.master_sql_col_map[field]
                    if str(data).find('<=>'):
                        dates_data = str(data).split('<=>')
                        start_date = dates_data[0]
                        end_date = dates_data[1]
                        self.params_for_sql[old_field + '_start_date'] = start_date
                        self.params_for_sql[old_field + '_end_date'] = end_date
                        filter_str = filter_fmt.format(field, old_field + '_start_date', old_field + '_end_date')
                        # TODO implement today i.e single date

                elif op == 'dteq':
                    # operation for searching date time range in grid
                    old_field = str(field).replace(' ', '_')
                    field = self.master_sql_col_map[field]
                    if str(data).find('<=>'):
                        dates_data = str(data).split('<=>')
                        start_date = dates_data[0]
                        end_date = dates_data[1]
                        self.params_for_sql[old_field + '_start_date_time'] = start_date
                        self.params_for_sql[old_field + '_end_date_time'] = end_date
                        filter_str = filter_fmt.format(field, old_field + '_start_date_time', old_field + '_end_date_time')

                elif op == 'dob':
                    # operation for searching date range in grid
                    old_field = str(field).replace(' ', '_')
                    field = self.master_sql_col_map[field]
                    if str(data).find('<=>'):
                        dates_data = str(data).split('<=>')
                        start_date = datetime.strptime(dates_data[0], "%Y-%m-%d").date()
                        end_date = datetime.strptime(dates_data[1], "%Y-%m-%d").date()
                        self.params_for_sql[old_field + '_start_date'] = start_date
                        self.params_for_sql[old_field + '_end_date'] = end_date
                        filter_str = filter_fmt.format(field, old_field + '_start_date', old_field + '_end_date')
                elif op == 'cns':
                    old_field = str(field).replace(' ', '_')
                    field = self.master_sql_col_map[field]
                    self.params_for_sql[old_field] = data
                    filter_str = filter_fmt.format(field, old_field)
                elif op in ['iin', 'niin']:
                    old_field = str(field).replace(' ', '_')
                    field = self.master_sql_col_map[field]
                    data = data.split(',')
                    new_param_arr = []
                    for item in data:
                        new_param_arr.append(int(item))
                    self.params_for_sql[old_field] = new_param_arr
                    filter_str = filter_fmt.format(field, old_field)
                elif op == 'hc':
                    field = self.master_sql_col_map[field]
                    filter_str = field

                elif op == '2dteqor':
                    # two fields matching same date time range.
                    old_field = str(field).replace(' ', '_').split('<=>')
                    old_field1 = old_field[0]
                    old_field2 = old_field[1]
                    field1 = self.master_sql_col_map[old_field1]
                    field2 = self.master_sql_col_map[old_field2]
                    if str(data).find('<=>'):
                        dates_data = str(data).split('<=>')
                        start_date = dates_data[0]
                        end_date = dates_data[1]
                        self.params_for_sql[old_field1 + '_start_date_time'] = start_date
                        self.params_for_sql[old_field1 + '_end_date_time'] = end_date
                        self.params_for_sql[old_field2 + '_start_date_time'] = start_date
                        self.params_for_sql[old_field2 + '_end_date_time'] = end_date
                        filter_str = filter_fmt.format(field1, old_field1 + '_start_date_time', old_field1 + '_end_date_time', field2 , old_field2 + '_start_date_time', old_field2 + '_end_date_time')

                elif op == '2deqor':
                    # eg. two fields matching same date
                    old_field = str(field).replace(' ', '_').split('<=>')
                    old_field1 = old_field[0]
                    old_field2 = old_field[1]
                    field1 = self.master_sql_col_map[old_field1]
                    field2 = self.master_sql_col_map[old_field2]
                    self.params_for_sql['2deqor_specific_date'] = str(data)
                    filter_str = filter_fmt.format(field1, field2, '2deqor_specific_date')

                else:
                    new_field_param_name = field + '-' + op
                    field = self.master_sql_col_map[field]
                    self.params_for_sql[new_field_param_name] = data
                    filter_str = filter_fmt.format(field, new_field_param_name)

                if _filters['groupOp'].upper() == 'OR':
                    additional_where_sql += ' OR ' + filter_str
                else:
                    additional_where_sql += ' AND ' + filter_str

        return additional_where_sql

    def group_by_items_sql(self, request):
        return self.group_by_query

    def sort_items_sql(self, grid_obj):
        sidx = grid_obj.get('sidx')
        if sidx is not None:
            sord = grid_obj.get('sord')
            order_by = ' order by %s %s ' % (self.master_sql_col_map[sidx],sord == 'desc' and 'desc' or '')
        else:
            order_by = ' order by %s %s ' % (self.default_sort_col, self.default_sort_ord)
        return order_by


class ReportGridEngine(ReportEngine):
    """
        generic grid
    """
    def __init__(self, view_type, generate_plan_rows=False, no_json_encoding=True):
        super(ReportGridEngine, self).__init__(view_type, generate_plan_rows, no_json_encoding)

    def build_select_query(self, grid_obj):
        """
            Build the select query based on the params.
        :param:
        :return:
        """

        select_query = 'SELECT '
        select_count_query = 'SELECT COUNT(*) '
        from_query = ''

        if self.view_type == reportManagerConstants.REPORT_BOOKING:
            self.default_sort_col = " b.updated_at "
            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKING_MASTER_SQL_WHERE_COLS_MAP
            self.group_by_query = ' group by b.id '

            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKING_MASTER_SQL_COLS)
            from_query = """
                            from
                            core_booking b
                            inner join core_bumperuser bu on b.user_id=bu.id
                            inner join core_bookingstatus bs on b.status_id=bs.id
                            inner join core_usercar uc on uc.id = b.usercar_id
                            left outer join core_bumperuser bu1 on b.assigned_to_id=bu1.id
                            left outer join core_bookingopsstatus bss on b.ops_status_id=bss.id
                            left outer join core_carmodel cm on uc.car_model_id=cm.id
                            left outer join core_carbrand cb on cm.brand_id=cb.id
                            left outer join core_workshop w on w.id = b.workshop_id
                        """

            from_query += " WHERE bu.phone is not null "
            if grid_obj['user'].groups.filter(name__in=['DriverManager', 'Driver']).exists() and not grid_obj['user'].groups.filter(name__in=['OpsManager', 'OpsAdmin']).exists():
                from_query += " and ((bs.flow_order_num >= 3 and bs.flow_order_num <= 10 and (b.ops_status_id is null or b.ops_status_id !=8)) " \
                              " or (bs.flow_order_num >= 19 and bs.flow_order_num < 22)) "

        elif self.view_type == reportManagerConstants.REPORT_BOOKING_HISTORY:
            self.default_sort_col = " b.updated_at "
            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKING_HISTORY_MASTER_SQL_WHERE_COLS_MAP
            self.group_by_query = ' '

            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKING_HISTORY_MASTER_SQL_COLS)
            from_query = """
                            from
                            core_historicalbooking b
                            inner join core_bumperuser bu on b.user_id=bu.id
                            inner join core_bookingstatus bs on b.status_id=bs.id
                            inner join core_usercar uc on uc.id = b.usercar_id
                            left outer join core_bumperuser bu1 on b.assigned_to_id=bu1.id
                            left outer join core_bumperuser bu2 on b.updated_by_id=bu2.id
                            left outer join core_bookingopsstatus bss on b.ops_status_id=bss.id
                            left outer join core_carmodel cm on uc.car_model_id=cm.id
                            left outer join core_carbrand cb on cm.brand_id=cb.id
                            left outer join core_workshop w on w.id = b.workshop_id
                        """

            from_query += " WHERE b.id > 0 "

        elif self.view_type == reportManagerConstants.REPORT_BOOKINGS_BY_USERS:
            self.default_sort_col = " bu.id "
            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKINGS_BY_USERS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKINGS_BY_USERS_MASTER_SQL_COLS)
            from_query = """
                            from core_bumperuser bu
                            left outer  join core_booking b on b.user_id=bu.id
                            left outer  join core_bookingstatus bs on bs.id=b.status_id
                        """

            from_query += """
                            WHERE not exists (select 1 from core_internalaccounts ia where ia.phone=bu.phone)
                            AND exists(select 1 from core_bumperuser_groups bug
                                inner join auth_group ag on ag.id=bug.group_id
                                where bug.bumperuser_id=bu.id and ag.name='BumperUser')
                            """

        elif self.view_type == reportManagerConstants.REPORT_USER:
            self.default_sort_col = " bu.id "
            self.group_by_query = ' group by bu.id '
            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_USER_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_USER_MASTER_SQL_COLS)
            from_query = """
                            from core_bumperuser bu
                            left outer join core_city c on bu.city_id = c.id
                            left outer join core_usercar uc on uc.user_id = bu.id
                            left outer join core_carmodel cm on uc.car_model_id = cm.id
                            left outer  join core_booking b on b.user_id=bu.id
                        """

            from_query += " WHERE bu.id>0 "

        elif self.view_type == reportManagerConstants.REPORT_NOTIFY_USER:
            self.default_sort_col = " bu.id "
            self.group_by_query = ' group by bu.id '
            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_NOTIFY_USER_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_NOTIFY_USER_MASTER_SQL_COLS)
            from_query = """
                            from core_bumperuser bu
                            left outer join core_city c on bu.city_id = c.id
                            left outer join core_usercar uc on uc.user_id = bu.id
                            left outer join core_carmodel cm on uc.car_model_id = cm.id
                            left outer  join core_booking b on b.user_id=bu.id
                        """

            from_query += " WHERE exists(select 1 from core_userdevices uds where uds.user_id=bu.id) "

        elif self.view_type == reportManagerConstants.REPORT_BOOKING_NOTIFICATIONS_SENT:
            self.default_sort_col = " m.id "
            self.group_by_query = ' group by m.id '

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKING_NOTIFICATIONS_SENT_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKING_NOTIFICATIONS_SENT_MASTER_SQL_COLS)
            from_query = """
                            from core_messages m
                            left outer join core_messageuser mu on mu.message_id=m.id
                            left outer join core_bumperuser bu1 on m.sent_by_id=bu1.id
                            left outer join core_notifications n on m.notification_id=n.id
                        """

            from_query += " WHERE m.id>1 "

        elif self.view_type == reportManagerConstants.REPORT_BOOKING_FOLLOWUPS:
            self.default_sort_col = " f.id "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKING_FOLLOWUPS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKING_FOLLOWUPS_MASTER_SQL_COLS)
            from_query = """
                            from core_followup f
                            inner join core_booking_followup bf on bf.followup_id = f.id
                            inner join core_booking b on b.id = bf.booking_id
                            inner join core_bumperuser bu on bu.id=f.updated_by_id
                            inner join core_bumperuser bu1 on b.user_id=bu1.id
                            inner join core_bookingstatus bs on bs.id=b.status_id
                        """

            from_query += " WHERE f.note is not null "

        elif self.view_type == reportManagerConstants.REPORT_INQUIRY_FOLLOWUPS:
            self.default_sort_col = " f.id "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_INQUIRY_FOLLOWUPS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_INQUIRY_FOLLOWUPS_MASTER_SQL_COLS)
            from_query = """
                            from core_followup f
                            inner join core_userinquiry_followup uif on uif.followup_id = f.id
                            inner join core_userinquiry ui on ui.id = uif.userinquiry_id
                            inner join core_bumperuser bu on bu.id=f.updated_by_id
                            inner join core_bumperuser bu1 on ui.user_id=bu1.id
                        """

            from_query += " WHERE f.note is not null "

        elif self.view_type == reportManagerConstants.REPORT_USER_INQUIRY:
            self.default_sort_col = " ui.id "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_USER_INQUIRY_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_USER_INQUIRY_MASTER_SQL_COLS)
            from_query = """
                            from core_userinquiry ui
                            inner join core_bumperuser bu on ui.user_id = bu.id
                            left outer join core_bumperuser bu1 on ui.assigned_to_id = bu1.id
                            left outer join core_carmodel cm on cm.id = ui.car_model_id
                            left outer join core_carbrand cb on cb.id = cm.brand_id
                        """

            from_query += " WHERE ui.id > 0 "

        elif self.view_type == reportManagerConstants.REPORT_BOOKING_IN_STATUS:
            self.default_sort_col = " bs.flow_order_num "
            self.default_sort_ord = " "
            self.group_by_query = ' group by bs.id '

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_BOOKING_IN_STATUS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_BOOKING_IN_STATUS_MASTER_SQL_COLS)
            from_query = """
                            from core_booking b
                            inner join core_bookingstatus bs on bs.id = b.status_id
                        """

            from_query += " WHERE b.id > 0 "

        elif self.view_type == reportManagerConstants.REPORT_USER_INQUIRY_IN_STATUS:
            self.default_sort_col = " ui.status "
            self.default_sort_ord = " "
            self.group_by_query = ' group by ui.status '

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_USER_INQUIRY_IN_STATUS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_USER_INQUIRY_IN_STATUS_MASTER_SQL_COLS)
            from_query = """
                            from core_userinquiry ui
                        """

            from_query += " WHERE ui.id > 0 "

        elif self.view_type == reportManagerConstants.REPORT_WORKSHOP_LIVE:
            self.default_sort_col = " b.id "
            self.default_sort_ord = " "
            self.group_by_query = ' '

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_WORKSHOP_LIVE_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_WORKSHOP_LIVE_MASTER_SQL_COLS)
            from_query = """
                            FROM core_booking b
                            inner join core_bumperuser bu ON b.user_id = bu.id
                            inner join core_bookingstatus bs ON bs.id = b.status_id
                            inner join core_workshop w ON w.id = b.workshop_id
                            inner join core_usercar AS uc ON uc.id = b.usercar_id
                            inner join core_carmodel cm ON cm.id=uc.car_model_id
                            inner join core_city c on c.id=b.city_id
                            left outer join core_bookingopsstatus bos ON bos.id = b.ops_status_id
                            left outer join core_bumperuser buw ON b.workshop_asst_mgr_id = buw.id
                        """

            from_query += """
                            WHERE not exists(SELECT 1 FROM core_internalaccounts ia WHERE ia.phone=bu.phone)
                            AND exists (SELECT 1 FROM core_bookingpackage bp
                                            inner join core_packageprice pp ON pp.id=bp.package_id
                                            inner join core_package p ON pp.package_id=p.id
                                            WHERE bp.booking_id=b.id AND p.category in (2,3) limit 1)
                            AND bs.flow_order_num >= 9
                            AND bs.flow_order_num < 20
                        """

        elif self.view_type == reportManagerConstants.REPORT_SUMMARY_PICKED:
            self.default_sort_col = " b.id "
            self.default_sort_ord = " "
            self.group_by_query = " "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_SUMMARY_PICKED_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_SUMMARY_PICKED_MASTER_SQL_COLS)
            from_query = """
                            FROM core_booking b
                            inner join core_bumperuser bu ON b.user_id = bu.id
                            inner join core_bookingstatus bs on bs.id = b.status_id
                        """

            from_query += """
                            WHERE not exists(SELECT 1 FROM core_internalaccounts ia WHERE ia.phone=bu.phone)
                            AND bu.phone is not null
                            AND bs.flow_order_num >= 9
                            AND b.status_id !=24
                            AND b.return_reason_id is null
                            AND b.rework_booking_id is null
                            AND exists(select 1 from core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
        inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id and p.category in (2,3) limit 1)
                        """

        elif self.view_type == reportManagerConstants.REPORT_SUMMARY_TO_BE_PICKED:
            self.default_sort_col = " b.id "
            self.default_sort_ord = " "
            self.group_by_query = " "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_SUMMARY_TO_BE_PICKED_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_SUMMARY_TO_BE_PICKED_MASTER_SQL_COLS)
            from_query = """
                            FROM core_booking b
                            inner join core_bumperuser bu ON b.user_id = bu.id
                            inner join core_bookingstatus bs on bs.id = b.status_id
                        """

            from_query += """
                            WHERE not exists(SELECT 1 FROM core_internalaccounts ia WHERE ia.phone=bu.phone)
                            AND bu.phone is not null
                            AND b.return_reason_id is null
                            AND b.rework_booking_id is null
                            AND bs.flow_order_num = 3 and (b.ops_status_id is null or b.ops_status_id !=8)
                            AND exists(select 1 from core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
        inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id and p.category in (2,3) limit 1)
                        """

        elif self.view_type == reportManagerConstants.REPORT_ALERTS_RAISED:

            self.default_sort_col = " ta.resolved,ta.id desc"
            self.default_sort_ord = " "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_ALERTS_RAISED_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_ALERTS_RAISED_MASTER_SQL_COLS)
            from_query = """
                            FROM core_teamalert ta
                            inner join core_teamalertreason tar ON ta.alert_reason_id = tar.id
                            inner join core_bumperuser bu on ta.updated_by_id = bu.id
                            left outer join core_workshop w on ta.workshop_id = w.id
                        """

        elif self.view_type == reportManagerConstants.REPORT_SCRATCH_FINDER_USERS:

            self.default_sort_col = " sfu.date_joined"
            self.default_sort_ord = " desc "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_SCRATCH_FINDER_USERS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_SCRATCH_FINDER_USERS_MASTER_SQL_COLS)
            from_query = """
                            FROM core_bumperuser sfu
                        """

            from_query += """
                            WHERE exists(select 1 from core_bumperuser_groups bug
                                inner join auth_group ag on ag.id=bug.group_id
                                where bug.bumperuser_id=sfu.id and ag.name='ScratchFinder')
                        """

        elif self.view_type == reportManagerConstants.REPORT_SCRATCH_FINDER_LEADS:

            self.default_sort_col = " sfl.created_at"
            self.default_sort_ord = " desc "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_SCRATCH_FINDER_LEADS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_SCRATCH_FINDER_LEADS_MASTER_SQL_COLS)
            from_query = """
                            FROM core_scratchfinderlead sfl
                            inner join core_bumperuser bu on bu.id = sfl.user_id
                            left outer join core_carmodel cm on sfl.car_model_id=cm.id
                            left outer join core_carbrand cb on cm.brand_id=cb.id
                            left outer join core_bumperuser bu1 on bu1.id = sfl.updated_by_id
                            left outer join core_media m on m.id= sfl.media_id
                        """

        elif self.view_type == reportManagerConstants.REPORT_FEEDBACK_BY_CUSTOMER:

            self.default_sort_col = " bcf.id"
            self.default_sort_ord = " desc "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_FEEDBACK_BY_CUSTOMER_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_FEEDBACK_BY_CUSTOMER_MASTER_SQL_COLS)
            from_query = """
                            FROM core_bookingcustfeedback bcf
                            inner join core_booking b on b.id = bcf.booking_id
                            inner join core_bumperuser bu on bu.id = b.user_id
                        """

        elif self.view_type == reportManagerConstants.REPORT_FEEDBACK_BY_OPS:

            self.default_sort_col = " bf.id"
            self.default_sort_ord = " desc "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_FEEDBACK_BY_OPS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_FEEDBACK_BY_OPS_MASTER_SQL_COLS)
            from_query = """
                            FROM core_bookingfeedback bf
                            inner join core_booking b on b.id = bf.booking_id
                            inner join core_bumperuser bu on bu.id = b.user_id
                        """

        elif self.view_type == reportManagerConstants.REPORT_CREW_DASHBOARD_PICKUP:

            self.default_sort_col = " b.id"
            self.default_sort_ord = " "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_CREW_DASHBOARD_PICKUP_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_CREW_DASHBOARD_PICKUP_MASTER_SQL_COLS)
            from_query = """
                            FROM core_booking b
                            inner join core_bumperuser bu ON bu.id = b.user_id
                            inner join bumper2.core_bookingstatus bs ON bs.id = b.status_id
                            left outer join bumper2.core_bookingopsstatus bos ON bos.id = b.ops_status_id
                            left outer join bumper2.core_workshop w ON w.id = b.workshop_id
                            left outer join bumper2.core_bookingaddress bap on bap.booking_id=b.id and bap.type=1
                            left outer join bumper2.core_address ap on ap.id=bap.address_id
                            left outer join bumper2.core_bookingaddress bad on bad.booking_id=b.id and bad.type=2
                            left outer join bumper2.core_address ad on ad.id=bad.address_id
                            left outer join bumper2.core_bumperuser bup on bup.id=b.pickup_driver_id
                            left outer join bumper2.core_bumperuser bud on bud.id=b.drop_driver_id
                        """

            from_query += """
                            WHERE not exists(SELECT 1 FROM bumper2.core_internalaccounts ia WHERE ia.phone=bu.phone)
                              AND bs.flow_order_num >= 3
                              AND b.status_id !=24
                              AND (b.ops_status_id is null or b.ops_status_id !=8)
                        """

        elif self.view_type == reportManagerConstants.REPORT_PART_DOCS:

            self.default_sort_col = " bpd.id"
            self.default_sort_ord = " desc "

            # set the where columns that will be used if server side filtering or sorting is used.
            self.master_sql_col_map = reportManagerConstants.REPORT_PART_DOCS_MASTER_SQL_WHERE_COLS_MAP
            # select columns
            select_query += ','.join(reportManagerConstants.REPORT_PART_DOCS_MASTER_SQL_COLS)
            from_query = """
                            from core_bookingpartdoc bpd
                              inner join core_partdocstatus pds on pds.id=bpd.status_id
                              inner join core_bookingpackagepanel bpp on bpp.id=bpd.booking_part_id
                              inner join core_bookingpackage bp on bp.id=bpp.booking_package_id
                              inner join core_booking b on b.id=bp.booking_id
                              inner join core_bumperuser bu on bu.id=b.user_id
                              inner join core_city c on c.id=b.city_id
                              inner join core_carpanelprice cpp on cpp.id=bpp.panel_id
                              inner join core_carpanel cp on cp.id=cpp.car_panel_id
                              inner join core_usercar uc on uc.id=b.usercar_id
                              inner join core_carmodel cm on cm.id=uc.car_model_id
                              inner join core_carbrand cb on cb.id=cm.brand_id
                              left outer join core_carmodelvariant cmv on cmv.id = uc.variant_id
                        """

            from_query += """
                            WHERE not exists(SELECT 1 FROM bumper2.core_internalaccounts ia WHERE ia.phone=bu.phone)
                        """

        select_query += from_query
        select_count_query += from_query
        return select_query, select_count_query




