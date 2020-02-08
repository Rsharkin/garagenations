/**
 * Created by Indy on 03/03/17.
 */
angular.module('ops.views.scratchFinders',[
    'ops.services.common'
]).controller('ScratchFindersCtrl', function(CommonService, $uibModal, $scope){
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
    });

    function loadData(){
        var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];
        CommonService.getReportData('report_scratch_finder_users', filters)
            .then(function (data) {
                if(data){
                    self.sfu = data.rows;
                    self.gridOptions.rowData = data.rows;
                    self.gridOptions.api.setRowData(data.rows);
                }else{
                    sweetAlert("Oops...", "Failed to Load SFU", "error");
                }
            });
    }
    loadData();

    var render_action_col = function(params){
        return '<a ng-click="scratchFindersCtrl.showReferredList('+params.data.id+', \''+params.data.name+'\')">'+params.data.referred+'</a>';
    };

    var columnDefs = [
        {headerName: "Name", field: "name", width: 150, cellClass: 'text-center'},
        {headerName: "Phone", field: "phone", width: 100, cellClass: 'text-center'},
        {headerName: "Email", field: "email", width: 200, cellClass: 'text-center'},
        {headerName: "# Referred", field: "referred", cellClass: 'text-center', filter: 'number', cellRenderer:render_action_col},
        {headerName: "# Converted", field: "converted", cellClass: 'text-center'},
        {headerName: "Date Joined", field: "date_joined"},
        {headerName: "Source", field: "source", width: 100},
        {headerName: "Ad Source", field: "utm_source", width: 100},
        {headerName: "Ad Medium", field: "utm_medium", width: 100},
        {headerName: "Ad Campaign", field: "utm_campaign", width: 100}
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

        if (self.extraFilters.dateRangeObj && (moment(node.data.date_joined + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.date_joined + ' +0530') > self.extraFilters.dateRangeObj.endDate)) {
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

    function showReferredList(referrerId, referrerName) {
        var modalInstance = $uibModal.open({
            templateUrl: 'views/scratch-finder-referred-list.html',
            controller: ScratchFinderReferredListCtrl,
            controllerAs: 'referredListCtrl',
            size:'lg',
            resolve: {
                referrerId: function () {
                    return referrerId;
                },
                referrerName: function () {
                    return referrerName;
                },
                sfStatuses: function(){
                    return self.sflStatuses;
                }
            }
        });
        modalInstance.result.then(function () {

        });
    }

    self.showReferredList = showReferredList;
    self.externalFilterChanged = externalFilterChanged;
});