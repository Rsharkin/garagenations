/**
 * Created by Indy on 10/03/17.
 */
angular.module('ops.views.reportBookingFeedbackOps',[
    'ops.services.common'
])
    .controller('ReportBookingFeedbackOpsCtrl', function(CommonService, $scope){
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
            CommonService.getReportData('report_feedback_by_ops', filters)
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

        var render_bumper_app_col = function(params){
            if(params.data.bumper_app === 2){
                return '<span><i class="fa fa-lg fa-smile-o text-success"></i></span>';
            }
            return '<span><i class="fa fa-lg fa-frown-o text-danger"></i></span>';
        };

        var render_pick_drop_service_col = function(params){
            if(params.data.pick_drop_service === 2){
                return '<span><i class="fa fa-lg fa-smile-o text-success"></i></span>';
            }
            return '<span><i class="fa fa-lg fa-frown-o text-danger"></i></span>';
        };

        var render_customer_care_col = function(params){
            if(params.data.customer_care === 2){
                return '<span><i class="fa fa-lg fa-smile-o text-success"></i></span>';
            }
            return '<span><i class="fa fa-lg fa-frown-o text-danger"></i></span>';
        };

        var render_work_quality_col = function(params){
            if(params.data.work_quality === 2){
                return '<span><i class="fa fa-lg fa-smile-o text-success"></i></span>';
            }
            return '<span><i class="fa fa-lg fa-frown-o text-danger"></i></span>';
        };

        var render_value_for_money_col = function(params){
            if(params.data.value_for_money === 2){
                return '<span><i class="fa fa-lg fa-smile-o text-success"></i></span>';
            }
            return '<span><i class="fa fa-lg fa-frown-o text-danger"></i></span>';
        };

        var columnDefs = [
            {headerName: "Booking Id", field: "booking_id", width: 125, cellClass: 'text-center', filter: 'number', cellRenderer:render_action_col},
            {headerName: "App", field: "bumper_app",cellClass: 'text-center', width: 135, cellRenderer:render_bumper_app_col},
            {headerName: "Experience", field: "experience_rating",cellClass: 'text-center', width: 135},
            {headerName: "Pickup", field: "pick_drop_service",cellClass: 'text-center', width: 135, cellRenderer:render_pick_drop_service_col},
            {headerName: "Customer Care", field: "customer_care",cellClass: 'text-center', width: 125, cellRenderer:render_customer_care_col},
            {headerName: "Work Quality", field: "work_quality",cellClass: 'text-center', width: 125, cellRenderer:render_work_quality_col},
            {headerName: "Value For Money", field: "value_for_money",cellClass: 'text-center', width: 150, cellRenderer:render_value_for_money_col},
            {headerName: "WOW", field: "wow_moment",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Any Suggestions", field: "any_suggestions",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Feedback Remarks", field: "feedback_remarks",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Issues", field: "customer_issue",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Issues", field: "customer_issue",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Ops Remarks", field: "customer_relation_remarks",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
            {headerName: "Referrals", field: "referrals",cellClass: 'text-center', cellStyle: {'white-space': 'normal'}},
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
            suppressContextMenu:true,
            suppressCellSelection:true,
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