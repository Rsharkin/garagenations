angular.module('ops.views.bookings', [
    'ops.services.common'
])
    .controller('BookingCtrl', function BookingCtrl(CommonService, $scope, UserService){
        var self = this;

        self.extraFilters={};
        self.showAllBookings = false;
        self.cities = CommonService.getSelectedCities();

        // TODO Inder Use city from user selection on top
        CommonService.getMasterData().then(function(res){
            self.workshops = res.workshops;
            self.internalAccounts = res.internal_accounts;
        });

        function loadBookings(){
            if(self.gridOptions){
                self.gridOptions.api.showLoadingOverlay();
            }
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
            if(!self.showAllBookings){
                filters.push({ 'op': 'niin', 'field': 'status_id', 'data': '23' });
                filters.push({ 'op': 'niin', 'field': 'ops_status_id', 'data': '28' });
            }

            CommonService.getReportData('report_booking', filters)
                .then(function (data) {
                    if(data){
                        self.bookings = data.rows;
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                        restoreFilterModel();

                    }else{
                        sweetAlert("Oops...", "Failed to Load bookings", "error");
                    }
                    if(self.gridOptions) {
                        self.gridOptions.api.hideOverlay();
                    }
                });
        }
        loadBookings();

        var perm_see_cust_num = UserService.doesUserHasPermission('core.see_customer_number');

        function getCustomerNumber(phoneNumber){
            if(phoneNumber){
                //console.log('perm_see_cust_num->', perm_see_cust_num);
                if(UserService.dontShowCustomerNum && !perm_see_cust_num){
                    return "XXXXXX" + phoneNumber.substr(-4);
                }
            }
            return phoneNumber;
        }

        var render_action_col = function(params){
            return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.id+'})" target="_blank">'+params.data.id+'</a>' + (params.data.escalated_flag ?'<br><i class="fa fa-flag text-danger"></i>':'');
        };
        var render_rework_col = function(params){
            if(params.data.rework_booking_id){
                return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.rework_booking_id+'})" target="_blank">'+params.data.rework_booking_id+'</a>';
            }
            return '';
        };
        var render_user_col = function(params){
            return "<p><b>" + params.data.name + "</b></p><p>" + getCustomerNumber(params.data.phone) +' <a permission="[\'OpsAdmin\',\'OpsManager\',\'Caller\',\'CityCallCenterManager\', \'WorkshopManager\', \'WorkshopAssistantManager\',\'DriverManager\',\'ViewOnlyBooking\',\'MarketingTeam\']" ui-sref="base.recordings({phoneNumbers:'+params.data.phone+'})" target="_blank"><i class="fa fa-youtube-play"></i> Recording</a></p><p>'+ params.data.email + "</p>";
        };
        var render_car_col = function(params){
            return params.data.model +"<br>"+ params.data.brand;
        };
        var render_pickup_time_col = function(params){
            var to_display = (params.data.p_time?params.data.p_time:'');
            if (params.data.p_time_end?params.data.p_time_end:''){
                to_display = to_display + ' - ' + (params.data.p_time_end?params.data.p_time_end:'');
            }
            return to_display;
        };
        var render_end_time_col = function(params){
            var to_display = (params.data.d_time?params.data.d_time:'');
            if (params.data.d_time_end?params.data.d_time_end:''){
                to_display = to_display + ' - ' + (params.data.d_time_end?params.data.d_time_end:'');
            }
            return to_display;
        };
        var render_has_vas_package_col = function(params){
            if (params.data.has_vas_package){
                return '<span><img src="/static/admin/img/icon-yes.gif" alt="True"></span>';
            }else{
                return '<span><img src="/static/admin/img/icon-no.gif" alt="True"></span>';
            }
        };
        var render_is_returned_col = function(params){
            if (params.data.car_returned){
                return '<span><img src="/static/admin/img/icon-yes.gif" alt="True"></span>';
            }else{
                return '<span><img src="/static/admin/img/icon-no.gif" alt="True"></span>';
            }
        };
        var render_is_insurance_col = function(params){
            if (params.data.insurance_flag){
                return '<span><img src="/static/admin/img/icon-yes.gif" alt="True"></span>';
            }else{
                return '<span><img src="/static/admin/img/icon-no.gif" alt="True"></span>';
            }
        };

        var columnDefs = [
            {headerName: "Id", field: "id", width: 80, filter: 'number',cellRenderer:render_action_col},
            {headerName: "Next FollowUp", field: "next_followup", width: 110},
            {headerName: "Status", field: "status", width: 150},
            {headerName: "Ops Status", field: "ops_status", width: 150},
            {headerName: "Lead Quality", field: "lead_quality", width: 75},
            {headerName: "User", field: "user", width: 200,cellRenderer:render_user_col},
            {headerName: "Assigned To", field: "assigned_to", width: 150},
            {headerName: "Caller", field: "caller", width: 150},
            {headerName: "Created Dt", field: "created_at", width: 85},
            {headerName: "Updated Dt", field: "updated_at", width: 85},
            {headerName: "Created In", field: "created_in", width: 100},
            {headerName: "Created By", field: "created_by", width: 100},
            {headerName: "Rework Of", field: "rework_booking_id", width: 100,cellRenderer:render_rework_col},

            {headerName: "Car", field: "model", width: 125,cellRenderer:render_car_col},
            {headerName: "Source", field: "source", width: 125},
            {headerName: "Ad Source", field: "utm_source", width: 125},
            {headerName: "Ad Medium", field: "utm_medium", width: 125},
            {headerName: "Ad Campaign", field: "utm_campaign", width: 125},
            {headerName: "User Creation Time", field: "user_created_at", width: 125},
            {headerName: "Doorstep", field: "is_doorstep", width: 125},
            {headerName: "Panels", field: "num_of_panels", width: 125},
            {headerName: "VAS", field: "has_vas_package", width: 45,cellRenderer:render_has_vas_package_col},
            {headerName: "Packages", field: "packages", width: 125},

            {headerName: "Workshop", field: "workshop", width: 125},

            {headerName: "Pickup Time", field: "p_time", width: 110},
            {headerName: "Actual Pickup", field: "actual_pickup_time", width: 110},
            {headerName: "Drop Time", field: "d_time", width: 110},
            {headerName: "Estimate Delivery", field: "e_d_time"},
            {headerName: "Returned", field: "car_returned", cellRenderer:render_is_returned_col, width: 100},
            {headerName: "Insurance", field: "insurance_flag", cellRenderer:render_is_insurance_col, width: 100}
        ];


        self.gridOptions = {
            columnDefs: columnDefs,
            rowData: null,
            rowHeight: 75,
            enableColResize: true,
            enableSorting: true,
            suppressMultiSort: true,
            enableFilter: true,
            angularCompileRows: true,
            //pinnedColumnCount: 6,
            suppressRowClickSelection:true,
            suppressContextMenu:true,
            suppressCellSelection:true,
            onAfterFilterChanged: saveFilterModel,
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

        function isExternalFilterPresent() {
            return self.extraFilters && (self.extraFilters.dateRangeObj || self.extraFilters.removeInternal || self.extraFilters.workshops || self.extraFilters.showEscalated);
        }

        function doesExternalFilterPass(node) {
            var result = true;

            if(self.extraFilters && (self.extraFilters.workshops && self.extraFilters.workshops.length>0) && ! _.some(self.extraFilters.workshops,{'name':node.data.workshop})){
                return false;
            }
            if(self.extraFilters.dateRangeObj && (moment(node.data.created_at + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.created_at + ' +0530') > self.extraFilters.dateRangeObj.endDate)){
                return false;
            }
            if(self.extraFilters.removeInternal && _.indexOf(self.internalAccounts, node.data.phone) != -1){
                return false;
            }
            if(self.extraFilters.showEscalated && node.data.escalated_flag !== 1){
                return false;
            }
            return result;
        }

        function externalFilterChanged() {
            self.gridOptions.api.onFilterChanged();
        }
        self.date_range_options = {
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            eventHandlers: {'apply.daterangepicker': function(ev, picker) {
                self.extraFilters.dateRangeObj = picker;
                externalFilterChanged();
            }}
        };

        function exportInCsv(){
            var isAllowedToUserDetails = UserService.isUserInGroup(['DataAnalyst']);

            var params = {
                'processCellCallback': function(params) {
                    if(params.column.colId === 'user' && !isAllowedToUserDetails){
                        return params.node.data.name;
                    }
                    return params.value;
                }
            };
            self.gridOptions.api.exportDataAsCsv(params);
        }

        self.savedModel = null;
        self.savedFilters = '[]';

        function clearFilters() {
            self.gridOptions.api.setFilterModel(null);
            self.gridOptions.api.onFilterChanged();
            // $window.localStorage.bookingsFilters = null;
            self.savedModel = null;
        }

        function saveFilterModel() {
            self.savedModel = self.gridOptions.api.getFilterModel();

            /*if (Object.keys(self.savedModel || {})) {
             self.savedFilters = JSON.stringify(Object.keys(self.savedModel));
             $window.localStorage.bookingsFilters = JSON.stringify(self.savedModel);
             } else {
             self.savedFilters = '-none-';
             }*/
        }

        function restoreFilterModel() {
            // var savedModel = $window.localStorage.bookingsFilters;
            if(self.savedModel){
                self.gridOptions.api.setFilterModel(self.savedModel);
                self.gridOptions.api.onFilterChanged();
            }
        }

        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            loadBookings();
        });

        self.exportInCsv = exportInCsv;
        self.externalFilterChanged = externalFilterChanged;
        self.loadBookings = loadBookings;
        self.clearFilters = clearFilters;
        self.saveFilterModel = saveFilterModel;
        self.restoreFilterModel = restoreFilterModel;
    })
;
