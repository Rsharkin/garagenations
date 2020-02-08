/**
 * Created by Indy on 14/02/17.
 */
angular.module('ops.views.reportLiveWorkshop',[
    'ops.services.common',
    'ops.services.user'
]).controller('ReportWorkshopLiveCtrl', function ReportWorkshopLiveCtrl($scope, $state, $stateParams, CommonService,
                                                                          DTOptionsBuilder, $uibModal, $window,
                                                                        UserService ) {
        var self = this;
        var screenWidth = $window.innerWidth;
        self.summary = {
            'alerts':[]
        };
        self.extraFilters={};
        self.dtOptions = DTOptionsBuilder.newOptions()
            .withPaginationType('full_numbers')
            .withOption('lengthMenu', [25, 50, 100])
            .withOption('pageLength', 25)
        ;

        self.showEODActions =  new Date().getHours() >= 16;
        self.cities = CommonService.getSelectedCities();
        self.showOnlyAlertBookings = false;
        self.showOnlyCrewFailedQCAlertBookings = false;

        UserService.getWorkshopAssistantManager().then(function(res){
            self.assisstantManagers = res;
        });

        function getWorkshopData(){
            var filters = '';
            if(self.cities){
               filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
            }
            CommonService.getReportData('report_workshop_live', filters)
                .then(function (data) {
                    if(data){
                        self.workshop_data = data.rows;
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                        //setTimeout(function(){ restoreFilterModel(); }, 1000);
                        restoreFilterModel();

                        self.summary.num_of_cars = 0;
                        self.summary.num_of_cust_eta_miss = 0;
                        self.summary.num_of_workshop_eta_miss = 0;
                        self.summary.num_of_repair = 0;
                        self.summary.num_of_replace = 0;
                        self.summary.num_of_spare = 0;
                        self.summary.alert_ceta_less_weta = 0;
                        self.summary.alert_ceta_less_weta_list = [];
                        self.summary.alerts.crew_failed_qc = 0;
                        self.summary.alerts.crew_failed_qc_list = [];
                        self.summary.num_of_panels = _.reduce(self.workshop_data, function(sum, item) {
                            if(!sum){
                                sum=0;
                            }
                            if(item.customer_eta_failed == 1){
                                self.summary.num_of_cust_eta_miss +=1;
                            }
                            if(item.ceta_less_weta == 1){
                                self.summary.alert_ceta_less_weta +=1;
                                self.summary.alert_ceta_less_weta_list.push(item);
                            }
                            if(item.ops_status_id == 47){
                                self.summary.alerts.crew_failed_qc +=1;
                                self.summary.alerts.crew_failed_qc_list.push(item);
                            }
                            if(item.workshop_eta_failed == 1 && item.customer_eta_failed != 1){
                                self.summary.num_of_workshop_eta_miss +=1;
                            }
                            self.summary.num_of_cars += 1;

                            self.summary.num_of_repair += item.num_of_repair_panels;
                            self.summary.num_of_replace += item.num_of_replace_panels;
                            self.summary.num_of_spare += item.num_of_spare;

                            return sum  + parseFloat(item.num_of_panels);
                        }, null);
                    }else{
                        sweetAlert("Oops...", "Failed to Load bookings", "error");
                    }
                });
        }
        var render_action_col = function(params){
            return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.booking_id+'})" target="_blank">'+params.data.booking_id+'</a>';
        };
        var render_has_vas_package_col = function(params){
            if (params.data.has_vas_package){
                return '<span><img src="/static/admin/img/icon-yes.gif" alt="True"></span>';
            }else{
                return '<span><img src="/static/admin/img/icon-no.gif" alt="True"></span>';
            }
        };
        var render_rework_col = function(params){
            if (params.data.rework == 1){
                return '<span><img src="/static/admin/img/icon-yes.gif" alt="True"></span>';
            }else{
                return '<span><img src="/static/admin/img/icon-no.gif" alt="True"></span>';
            }
        };
        var render_workshop_eta_col = function(params){
            var eta = '';
            if(params.data.workshop_ETA ){
                eta = '<span>'+ params.data.workshop_ETA ;
            }
            if(params.data.num_changes_workshop_eta){
                eta += '(#'+ params.data.num_changes_workshop_eta +')';
            }
            if(eta){
                eta += '</span>';
            }
            return eta;
        };
        var render_cust_eta_col = function(params){
            var eta = '';
            if(params.data.customer_ETA ){
                eta = '<span>'+ params.data.customer_ETA ;
            }
            if(params.data.num_changes_customer_eta){
                eta += '(#'+ params.data.num_changes_customer_eta + ')';
            }
            if(eta){
                eta += '</span>';
            }
            return eta;
        };

        var render_eod_action = function(params){
            var actions = '<div>';
            if(self.showEODActions && params.data.is_eod_eta_done != 1){
                actions += '<input ' +
                    'type="button" ' +
                    'class="btn btn-sm btn-primary" ' +
                    'value="ETA" ' +
                    'ng-click="reportWorkshopLiveCtrl.updateETA('+ params.data.booking_id+',\''+ (params.data.workshop_ETA?params.data.workshop_ETA:'') +'\',\''+ (params.data.customer_ETA?params.data.customer_ETA:'') +'\')" />';
            }
            if(self.showEODActions && params.data.is_eod_message_done != 1){
                actions += '<input ' +
                    'type="button" ' +
                    'class="btn btn-sm btn-primary m-l-xs" ' +
                    'value="Message" ' +
                    'ng-click="reportWorkshopLiveCtrl.sendEODMessage('+ params.data.booking_id+',\''+ (params.data.customer_ETA?params.data.customer_ETA:'') +'\')" />';
            }
            actions += '<div>' +
                '<span>'+ (params.data.total_eta_to_do? 'ETA:' + params.data.num_eta_done +'/'+ params.data.total_eta_to_do:'') +'</span>' +
                ' <br> ' +
                '<span>EOD:'+ (params.data.num_eod_message_done?params.data.num_eod_message_done:'') + '/' + (params.data.total_eod_to_do?params.data.total_eod_to_do:'') +'</span>' +
                '</div>';
            return actions;
        };

        function render_last_update_time(params){
            if(params.data.last_update_from_workshop >= 1) {
                return '<span>' + params.data.last_update_from_workshop + '</span>';
            }else if(params.data.last_update_from_workshop === 0) {
                return '<span>' + 0 + '</span>';
            }
            return '';
        }

        var columnDefs = [
            {headerName: "ID", field: "booking_id", filter: 'number', cellRenderer:render_action_col},
            {headerName: "Car", field: "car", cellStyle: {'white-space': 'normal'}},
            {headerName: "# Panels", field: "num_of_panels"},
            {headerName: "VAS", field: "has_vas_package",cellRenderer:render_has_vas_package_col},
            {headerName: "Rework", field: "rework",cellRenderer:render_rework_col},
            {headerName: "Workshop", field: "workshop"},
            {headerName: "Pickup DT", field: "pickedUp_time", cellStyle: {'white-space': 'normal'}},
            {headerName: "Workshop ETA", field: "workshop_ETA", cellStyle: {'white-space': 'normal'},cellRenderer:render_workshop_eta_col},
            {headerName: "WS Update (hrs)", field: "last_update_from_workshop",cellRenderer:render_last_update_time},
            {headerName: "Customer ETA", field: "customer_ETA", cellStyle: {'white-space': 'normal'},cellRenderer:render_cust_eta_col},
            {headerName: "Status", field: "status", cellStyle: {'white-space': 'normal'}},
            {headerName: "Ops-Status", field: "ops_status", cellStyle: {'white-space': 'normal'}},
            {headerName: "EOD Action", field: "num_changes_customer_eta", cellRenderer:render_eod_action}
        ];

        self.savedModel = null;
        self.savedFilters = '[]';

        function clearFilters() {
            self.gridOptions.api.setFilterModel(null);
            self.gridOptions.api.onFilterChanged();
            $window.localStorage.liveDashboardFilters = null;
        }

        function saveFilterModel() {
            self.savedModel = self.gridOptions.api.getFilterModel();

            if (Object.keys(self.savedModel || {})) {
                self.savedFilters = JSON.stringify(Object.keys(self.savedModel));
                $window.localStorage.liveDashboardFilters = JSON.stringify(self.savedModel);
            } else {
                self.savedFilters = '-none-';
            }
        }

        function restoreFilterModel() {
            var savedModel = $window.localStorage.liveDashboardFilters;
            if(savedModel){
                self.gridOptions.api.setFilterModel(JSON.parse(savedModel));
                self.gridOptions.api.onFilterChanged();
            }
        }

        self.gridOptions = {
            columnDefs: columnDefs,
            rowData: null,
            rowHeight: 75,
            headerHeight: 55,
            enableColResize: true,
            enableSorting: true,
            suppressMultiSort: true,
            enableFilter: true,
            angularCompileRows: true,
            suppressRowClickSelection:true,
            suppressCellSelection:true,
            suppressContextMenu:true,
            //forPrint:true,
            getRowClass: function (params) {
                            if(params.data.customer_eta_failed == 1){
                                return 'cust-eta-fail-warning';
                            }else if(params.data.workshop_eta_failed == 1){
                                return 'workshop-eta-fail-warning';
                            }else if(params.data.done_before_workshop_eta_failed == 1){
                                return 'cust-eta-success';
                            }
                        },
            onAfterFilterChanged: saveFilterModel,
            onGridReady: function(event) {
                if(screenWidth > 700){
                    self.gridOptions.api.sizeColumnsToFit();
                }
            },
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

        self.getTableHeight = function() {
           var rowHeight = 75; // your row height
           var headerHeight = 75; // your header height
           return {
              height: (self.workshop_data.length * rowHeight + headerHeight) + "px"
           };
        };
        function externalFilterChanged() {
            self.gridOptions.api.onFilterChanged();
        }
        function isExternalFilterPresent() {
            return (self.extraFilters && self.extraFilters.assisstantManagers) || self.showOnlyAlertBookings || self.showOnlyCrewFailedQCAlertBookings;
        }

        function doesExternalFilterPass(node) {
            var result = true;

            if(self.extraFilters && (self.extraFilters.assisstantManagers && self.extraFilters.assisstantManagers.length>0) && ! _.some(self.extraFilters.assisstantManagers,{'name':node.data.workshop_asst_mgr})){
                return false;
            }
            if(self.showOnlyAlertBookings && ! _.some(self.summary.alert_ceta_less_weta_list,{'booking_id':node.data.booking_id})){
                return false;
            }
            if(self.showOnlyCrewFailedQCAlertBookings && ! _.some(self.summary.alerts.crew_failed_qc_list,{'booking_id':node.data.booking_id})){
                return false;
            }
            return result;
        }

        function getPickedSummaryThisWeek(){
            var filters = [{ 'op': 'deq', 'field': 'actual_pickup_time',
                'data': moment().startOf('week').format('YYYY-MM-DD') + '<=>' + moment().endOf('week').format('YYYY-MM-DD') },
                { 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            CommonService.getReportData('report_summary_picked', filters)
                .then(function (data) {
                    if(data){
                        self.thisWeekSummary = data.rows && data.rows.length ? data.rows[0]:[];
                        self.thisWeekSummary.start_dt = moment().startOf('week').format('DD-MMM');
                        self.thisWeekSummary.end_dt = moment().endOf('week').format('DD-MMM');
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }

        function getPickedSummaryForRemainingWeek(){
            var start_date = moment().format('YYYY-MM-DD HH:mm');
            var filters = [{ 'op': 'dteq', 'field': 'pickup_time',
                'data': start_date + '<=>' + moment().endOf('week').format('YYYY-MM-DD') + ' 23:59' },
                { 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            CommonService.getReportData('report_summary_to_be_picked', filters)
                .then(function (data) {
                    if(data){
                        self.remaningThisWeekSummary = data.rows && data.rows.length ? data.rows[0]:[];
                        if(self.remaningThisWeekSummary && !self.remaningThisWeekSummary.num_of_panels){
                            self.remaningThisWeekSummary.num_of_panels = 0;
                        }
                        self.remaningThisWeekSummary.start_dt = moment().format('DD-MMM HH:mm');
                        self.remaningThisWeekSummary.end_dt = moment().endOf('week').format('DD-MMM');
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }

        function updateETA(booking_id, workshop_eta, customer_eta) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/edit-eta.html',
                controller: SetETAModalInstanceCtrl,
                controllerAs: 'setETAModalInstanceCtrl',
                resolve: {
                    booking: function() {
                        return {
                            'id': booking_id,
                            'workshop_eta': workshop_eta,
                            'estimate_complete_time': customer_eta
                        };
                    },
                    is_daily_update: function () {
                        return true;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function sendEODMessage(booking_id, customer_eta) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/send-eod-notification.html',
                controller: SendEODModalInstanceCtrl,
                controllerAs: 'sendEODModalInstanceCtrl',
                resolve: {
                    booking: function() {
                        return {
                            'id': booking_id,
                            'estimate_complete_time': customer_eta
                        };
                    },
                    is_daily_update: function () {
                        return true;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        // listen for the event in the relevant $scope
        $scope.$on('bookingChanged', function (event, data) {
            getWorkshopData();
        });
        getWorkshopData();

        getPickedSummaryThisWeek();
        getPickedSummaryForRemainingWeek();

        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            getWorkshopData();
            getPickedSummaryThisWeek();
            getPickedSummaryForRemainingWeek();
        });

        function exportInCsv(){
            var params = {};
            self.gridOptions.api.exportDataAsCsv(params);
        }

        function showAlertBookings(){
            self.showOnlyAlertBookings = self.showOnlyAlertBookings !== true;
            externalFilterChanged();
        }
        function showCrewFailedQCAlertBookings(){
            self.showOnlyCrewFailedQCAlertBookings = self.showOnlyCrewFailedQCAlertBookings !== true;
            externalFilterChanged();
        }
        self.updateETA = updateETA;
        self.sendEODMessage = sendEODMessage;
        self.clearFilters = clearFilters;
        self.saveFilterModel = saveFilterModel;
        self.restoreFilterModel = restoreFilterModel;
        self.exportInCsv = exportInCsv;
        self.externalFilterChanged = externalFilterChanged;
        self.showAlertBookings = showAlertBookings;
        self.showCrewFailedQCAlertBookings = showCrewFailedQCAlertBookings;
    });