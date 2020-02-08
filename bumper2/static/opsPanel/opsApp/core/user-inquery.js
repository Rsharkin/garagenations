angular.module('ops.views.userInquiry', [
    'ops.services.common',
    'ops.services.user',
    'ops.services.booking',
    'ops.services.data'
])
    .controller('UserInquiryCtrl', function BookingCtrl(CommonService, $scope, UserService){
        var self = this;

        self.extraFilters={};
        self.showAllInquiry = false;

        self.cities = CommonService.getSelectedCities();
        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            loadData();
        });

        function loadData(){
            CommonService.getMasterData()
                .then(function (data) {
                    if(data){
                        self.inquiryStatus = data.user_inquiry_statuses;
                        self.internalAccounts = data.internal_accounts;

                        if(self.gridOptions){
                            self.gridOptions.api.showLoadingOverlay();
                        }
                        var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
                        if(!self.showAllInquiry){
                           filters.push({ 'op': 'niin', 'field': 'status', 'data': '4,6,8,9,10,11' });
                        }
                        CommonService.getReportData('report_user_inquiry', filters)
                            .then(function (data) {
                                if(data){
                                    self.bookings = data.rows;
                                    self.gridOptions.rowData = data.rows;
                                    self.gridOptions.api.setRowData(data.rows);
                                    restoreFilterModel();
                                }else{
                                    sweetAlert("Oops...", "Failed to Load data", "error");
                                }
                                if(self.gridOptions) {
                                    self.gridOptions.api.hideOverlay();
                                }
                            });
                    }else{
                        sweetAlert("Oops...", "Failed to Load master data", "error");
                    }
                });
        }
        loadData();
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
            return '<a ui-sref="base.userInquiry.editUserInquiry({userInquiryId:'+params.data.id+'})" target="_blank"><i class="fa fa-pencil"></i></a>';
        };
        var render_booking_col = function(params){
            return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.latest_booking+'})" target="_blank">'+ (params.data.latest_booking?params.data.latest_booking:'') +'</a>';
        };
        var render_user_col = function(params){
            return "<p><b>" + params.data.name + "</b></p><p>" + getCustomerNumber(params.data.phone) +' <a ui-sref="base.recordings({phoneNumbers:'+params.data.phone+'})" target="_blank"><i class="fa fa-youtube-play"></i> Recording</a></p><p>'+ params.data.email + "</p>";
        };
        var render_car_col = function(params){
            return params.data.model?params.data.model:'' +"<br>"+ params.data.brand?params.data.brand:'';
        };
        var render_followup_note_col = function(params){
            return "<p title='"+params.data.last_followup_note+"'>"+ (params.data.last_followup_note?params.data.last_followup_note:'') +"</p>";
        };
        var render_inquiry_col = function(params){
            return "<p title='"+params.data.inquiry+"'>"+ (params.data.inquiry?params.data.inquiry:'') +"</p>";
        };
        var render_reference_col = function(params){
            return "<p title='"+params.data.reference+"'>"+ (params.data.reference?params.data.reference:'') +"</p>";
        };
        var render_status_col = function(params){
            return self.inquiryStatus[params.data.status];
        };

        var columnDefs = [
            {headerName: "", field: "", width: 25,cellRenderer:render_action_col},
            {headerName: "Id", field: "id", width: 45, filter: 'number'},
            {headerName: "User", field: "user", width: 200,cellRenderer:render_user_col},
            {headerName: "Assigned To", field: "assigned_to", width: 125},
            {headerName: "Next Followup", field: "next_followup_date", width: 125},
            {headerName: "Status", field: "status", width: 100,cellRenderer:render_status_col},
            {headerName: "Lead Quality", field: "lead_quality", width: 100},
            {headerName: "Source", field: "source", width: 100},
            {headerName: "Campaign", field: "utm_campaign", width: 100},
            {headerName: "Car", field: "model", width: 125,cellRenderer:render_car_col},
            {headerName: "Booking Latest", field: "latest_booking", width: 100, cellRenderer:render_booking_col},
            {headerName: "Inquiry", field: "inquiry", width: 200, cellRenderer:render_inquiry_col},
            {headerName: "Reference", field: "reference", width: 100, cellRenderer:render_reference_col},
            {headerName: "Created Dt", field: "created_at", width: 150},
            {headerName: "Last Followup", field: "last_followup_note", width: 300, cellRenderer:render_followup_note_col},
            {headerName: "Last Followup On", field: "followup_created_at", width: 150}
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
            suppressCellSelection:true,
            suppressContextMenu:true,
            onAfterFilterChanged: saveFilterModel,
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

        function isExternalFilterPresent() {
            return self.extraFilters && ((self.extraFilters.status && self.extraFilters.status.length>0) || self.extraFilters.dateRangeObj || self.extraFilters.removeInternal);
        }

        function doesExternalFilterPass(node) {
            var result = true;

            if(self.extraFilters && (self.extraFilters.status && self.extraFilters.status.length>0) && _.indexOf(self.extraFilters.status, self.inquiryStatus[node.data.status]) == -1){
                return false;
            }
            if(self.extraFilters.dateRangeObj && (moment(node.data.created_at + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.created_at + ' +0530') > self.extraFilters.dateRangeObj.endDate)){
                return false;
            }
            if(self.extraFilters.removeInternal && _.indexOf(self.internalAccounts, node.data.phone) != -1){
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
                processCellCallback : function(params) {
                    if(params.column.colId === 'status'){
                        return self.inquiryStatus[params.value];
                    }else if(params.column.colId === 'user' && !isAllowedToUserDetails){
                        return params.node.data.name;
                    }else{
                        return params.value;
                    }
                }
            };
            self.gridOptions.api.exportDataAsCsv(params);
        }

        self.savedModel = null;
        self.savedFilters = '[]';

        function clearFilters() {
            self.gridOptions.api.setFilterModel(null);
            self.gridOptions.api.onFilterChanged();
            //$window.localStorage.userInquiryFilters = null;
            self.savedModel = null;
        }

        function saveFilterModel() {
            self.savedModel = self.gridOptions.api.getFilterModel();

            /*if (Object.keys(self.savedModel || {})) {
                self.savedFilters = JSON.stringify(Object.keys(self.savedModel));
                $window.localStorage.userInquiryFilters = JSON.stringify(self.savedModel);
            } else {
                self.savedFilters = '-none-';
            }*/
        }

        function restoreFilterModel() {
            if(self.savedModel){
                self.gridOptions.api.setFilterModel(self.savedModel);
                self.gridOptions.api.onFilterChanged();
            }
        }

        self.exportInCsv = exportInCsv;
        self.externalFilterChanged = externalFilterChanged;
        self.loadData = loadData;
        self.clearFilters = clearFilters;

    })
;