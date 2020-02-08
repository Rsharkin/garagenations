/**
 * Created by Indy on 03/03/17.
 */
angular.module('ops.views.allLeads',[
    'ops.services.common'
])
    .controller('AllLeadsCtrl', function(CommonService, $uibModal, $scope){
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
            self.sflStatuses = res.sfl_statuses;
            loadData();
        });

        function loadData(){
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
            CommonService.getReportData('report_scratch_finder_leads',filters)
                .then(function (data) {
                    if(data){
                        // console.log('sfu data', data);
                        self.sfu = data.rows;
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                    }else{
                        sweetAlert("Oops...", "Failed to Load SFU", "error");
                    }
                });
        }


        var render_action_col = function(params){
            return '<a ng-click="allLeadsCtrl.editLead('+params.data.id+', '+params.data.status+')">'+params.data.id+'</a>';
        };
        var render_car_col = function(params){
            return params.data.model +"<br>"+ params.data.brand;
        };
        var render_status_col = function(params){
            return self.sflStatuses[params.data.status];
        };
        var render_details_col = function(params){
            return (params.data.media_url?'<a href="' + params.data.media_url + '" target="_blank">Photo</a>':'') + (params.data.details?params.data.details:'');
        };

        var columnDefs = [
            {headerName: "Id", field: "id", width: 45, filter: 'number',cellRenderer:render_action_col, cellClass: 'text-center'},
            {headerName: "Name", field: "name", width: 150, cellClass: 'text-center'},
            {headerName: "Phone", field: "phone", width: 100, cellClass: 'text-center'},
            {headerName: "Referrer", field: "referrer_name", width: 100, cellClass: 'text-center'},
            {headerName: "Status", field: "status", width: 150, cellClass: 'text-center', cellRenderer:render_status_col},
            {headerName: "Detail", field: "detail", cellRenderer:render_details_col},
            {headerName: "Car", field: "model", width: 125,cellRenderer:render_car_col},
            {headerName: "Booking", field: "booking_status", width: 125},
            {headerName: "Inquiry", field: "inquiry_status", width: 125},
            {headerName: "Updated By", field: "updated_by", width: 125},
            {headerName: "Created Dt", field: "created_at", width: 125}
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

            /*if (self.extraFilters.removeInternal && _.indexOf(self.internalAccounts, node.data.phone) !== -1) {
             return false;
             }*/

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

        function editLead(leadId, currentStatus) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/edit-scratch-finder-lead.html',
                controller: EditScratchFinderLead,
                controllerAs: 'sfModalCtrl',
                resolve: {
                    leadId: function () {
                        return leadId;
                    },
                    currentStatus: function () {
                        return currentStatus;
                    },
                    sfStatuses: function(){
                        return self.sflStatuses;
                    }
                }
            });
            modalInstance.result.then(function () {
                loadData();
            });
        }

        self.externalFilterChanged = externalFilterChanged;
        self.editLead = editLead;
    })
;
