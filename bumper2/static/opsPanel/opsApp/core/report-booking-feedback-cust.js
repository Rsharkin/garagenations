/**
 * Created by Indy on 10/03/17.
 */
angular.module('ops.views.reportBookingFeedbackCustomer',[
    'ops.services.common'
])
    .controller('ReportBookingFeedbackCustCtrl', function(CommonService, $scope){
        var self = this;
        self.extraFilters = {};
        self.cities = CommonService.getSelectedCities();
        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            loadData();
        });

        CommonService.getMasterData().then(function(res){
            self.internalAccounts = res.internal_accounts;
        });

        function loadData(){
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
            CommonService.getReportData('report_feedback_by_customer', filters)
                .then(function (data) {
                    if(data){
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                    }else{
                        sweetAlert("Oops...", "Failed to Load Feedback by user", "error");
                    }
                });
        }
        loadData();

        var render_action_col = function(params){
            return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.booking_id+'})" target="_blank">'+params.data.booking_id+'</a>';
        };

        var columnDefs = [
            {headerName: "Booking Id", field: "booking_id", width: 125, cellClass: 'text-center', filter: 'number', cellRenderer:render_action_col},
            {headerName: "Booking Experience", field: "booking_experience",cellClass: 'text-center', width: 135},
            {headerName: "Pickup Experience", field: "pickup_experience",cellClass: 'text-center', width: 135},
            {headerName: "Customer Care", field: "customer_care",cellClass: 'text-center', width: 125},
            {headerName: "Work Quality", field: "work_quality",cellClass: 'text-center', width: 125},
            {headerName: "Value For Money", field: "value_for_money",cellClass: 'text-center', width: 150},
            {headerName: "Any Suggestions", field: "any_suggestions",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Submitted On", field: "created_at",cellClass: 'text-center'}
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
            suppressRowClickSelection:true,
            suppressCellSelection:true,
            suppressContextMenu:true,
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

        function isExternalFilterPresent() {
            return self.extraFilters && (self.extraFilters.dateRangeObj || self.extraFilters.removeInternal);
        }

        function doesExternalFilterPass(node) {
            var result = true;

            if (self.extraFilters.dateRangeObj && (moment(node.data.created_at + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.created_at + ' +0530') > self.extraFilters.dateRangeObj.endDate)) {
                return false;
            }

            if (self.extraFilters.removeInternal && _.indexOf(self.internalAccounts, node.data.phone) !== -1) {
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

        self.externalFilterChanged = externalFilterChanged;
    });