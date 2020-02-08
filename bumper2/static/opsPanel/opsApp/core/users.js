angular.module('ops.views.users', [
    'ops.services.common'
])
    .controller('UsersCtrl', function UsersCtrl(CommonService, UserService){
        var self = this;
        self.extraFilters = {};

        CommonService.getMasterData().then(function(res){
            self.internalAccounts = res.internal_accounts;
            self.userSources = res.new_sources;
        });

        function loadUsers(filters) {
            CommonService.getReportData('report_user', filters)
                .then(function (data) {
                    if (data) {
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                    } else {
                        sweetAlert("Oops...", "Failed to Users", "error");
                    }
                });
        }
        loadUsers();
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
        var render_is_otp_validated_col = function (params) {
            var html = '<p class="text-center"><img src="/static/admin/img/icon-yes.gif" alt="True"></p>';
            if(!params.data.is_otp_validated) {
                html = '<p class="text-center"><img src="/static/admin/img/icon-no.gif" alt="True"></p>';
            }
            return html;
        };

        var render_app_install_col = function (params) {
            var html = '<p class="text-center"><img src="/static/admin/img/icon-yes.gif" alt="True"></p>';
            if(!params.data.app_install){
                html = '<p class="text-center"><img src="/static/admin/img/icon-no.gif" alt="True"></p>';
            }
            return html;
        };

        var render_car_col = function(params){
            if(params.data.car){return '<p class="text-center">' + params.data.car + '</p> <p class="text-center">' + params.data.car_fuel_type + '</p>';}else{ return '';}
        };

        var render_recording_col = function(params){
            if(params.data.phone){return '<a ui-sref="base.recordings({phoneNumbers:'+params.data.phone+'})" target="_blank"><i class="fa fa-youtube-play"></i> Recording</a>';}else{ return '';}
        };
        var render_bookings_col = function(params){
            var items = params.data.latest_booking? params.data.latest_booking.split(','):'';
            if(items){
                return '<a ui-sref="base.editBooking({bookingId:'+items[0]+'})" target="_blank">[ID:'+ items[0] +'] ' + items[1] + '</a><br> ';
            }else{
                return '';
            }
        };
        var render_inquiry_col = function(params){
            if(params.data.latest_inquiry){
                return '<a ui-sref="base.userInquiry.editUserInquiry({userInquiryId:'+ params.data.latest_inquiry +'})" target="_blank">[ID:'+ params.data.latest_inquiry + ']</a><br> ';
            }else{
                return '';
            }
        };
        var render_phone_col = function(params){
            return getCustomerNumber(params.data.phone);
        };
        var columnDefs = [
            //{headerName: "", field: "", width: 75},
            {headerName: "ID", field: "id", width: 58},
            {headerName: "OTP", field: "is_otp_validated", width: 58, cellRenderer: render_is_otp_validated_col},
            {headerName: "Name", field: "name", width: 150},
            {headerName: "Phone", field: "phone", width: 100, cellRenderer: render_phone_col},
            {headerName: "Email", field: "email", width: 200},
            {headerName: "Recordings", field: "phone", width: 100, cellRenderer: render_recording_col},
            {headerName: "App Installed", field: "app_install", width: 110, cellRenderer: render_app_install_col},
            {headerName: "City", field: "city", width: 85},
            {headerName: "Car", field: "car", width: 85, cellRenderer: render_car_col},
            {headerName: "Source", field: "source", width: 100},
            {headerName: "Ad Source", field: "utm_source", width: 100},
            {headerName: "Ad Medium", field: "utm_medium", width: 100},
            {headerName: "Ad Campaign", field: "utm_campaign", width: 100},
            {headerName: "# Bookings", field: "bookings", cellClass: 'text-center'},
            {headerName: "Latest Booking", field: "latest_booking", cellRenderer: render_bookings_col},
            {headerName: "Inquiry", field: "inquiries", cellRenderer: render_inquiry_col},
            {headerName: "Date Joined", field: "date_joined"}

        ];

        function isExternalFilterPresent() {
            //console.log('Changes in sources->',self.extraFilters.source );
            return self.extraFilters && ((self.extraFilters.source && self.extraFilters.source.length > 0) || self.extraFilters.dateRangeObj || self.extraFilters.removeInternal);
        }
        function doesExternalFilterPass(node) {
            var result = true;

            if (self.extraFilters && (self.extraFilters.source && self.extraFilters.source.length > 0) && _.indexOf(self.extraFilters.source,  node.data.source) === -1) {
                return false;
            }
            if (self.extraFilters.dateRangeObj && (moment(node.data.date_joined + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.date_joined + ' +0530') > self.extraFilters.dateRangeObj.endDate)) {
                return false;
            }
            if (self.extraFilters.removeInternal && _.indexOf(self.internalAccounts, node.data.phone) !== -1) {
                return false;
            }
            return result;
        }
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
            getRowClass: function (params) {
                if (!params.data.name || !params.data.is_otp_validated){
                    return 'row-warning';
                }
            },
            suppressRowClickSelection: true,
            suppressCellSelection: true,
            suppressContextMenu:true,
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

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
        function exportInCsv() {
            var isAllowedToUserDetails = UserService.isUserInGroup(['DataAnalyst']);
            var params = {
                'processCellCallback': function(params) {
                    if((params.column.colId === 'phone' || params.column.colId === 'email' || params.column.colDef.headerName === 'Recordings') && !isAllowedToUserDetails){
                        return '';
                    }
                    return params.value;
                }
            };
            self.gridOptions.api.exportDataAsCsv(params);
        }

        self.exportInCsv = exportInCsv;
        self.externalFilterChanged = externalFilterChanged;
    })
;
