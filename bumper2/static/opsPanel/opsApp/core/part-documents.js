/**
 * Created by Indy on 20/07/17.
 */
angular.module('ops.views.partDocs', [
    'ops.services.common'
])
    .controller('PartDocsCtrl', function PartDocsCtrl(CommonService, $scope, UserService){
        var self = this;

        self.extraFilters={};
        self.cities = CommonService.getSelectedCities();

        function loadPartDocs(){
            if(self.gridOptions){
                self.gridOptions.api.showLoadingOverlay();
            }
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            CommonService.getReportData('report_part_docs', filters)
                .then(function (data) {
                    if(data){
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);

                    }else{
                        sweetAlert("Oops...", "Failed to Load Parts", "error");
                    }
                    if(self.gridOptions) {
                        self.gridOptions.api.hideOverlay();
                    }
                });
        }
        loadPartDocs();

        var render_action_col = function(params){
            return '<a ui-sref="base.partDocs.details({partDocId:'+params.data.id+',bookingId:'+ params.data.booking_id +'})" target="_blank">'+params.data.id+'</a>';
        };
        var render_booking_col = function(params){
            return '<a ui-sref="base.bookings.editBooking.summary({bookingId:'+params.data.booking_id+'})" target="_blank">'+params.data.booking_id+'</a>';
        };

        var columnDefs = [
            {headerName: "Id", field: "id", width: 45, filter: 'number',cellRenderer:render_action_col},
            {headerName: "Booking", field: "booking_id", width: 125,cellRenderer:render_booking_col},
            {headerName: "Part", field: "panel_name", width: 150},
            {headerName: "Brand", field: "car_brand", width: 110},
            {headerName: "Model", field: "car_model", width: 110},
            {headerName: "Variant", field: "car_variant", width: 100},
            {headerName: "Year", field: "car_year_of_manufacture", width: 100},
            {headerName: "Status", field: "doc_status", width: 110},
            {headerName: "Quote ETA", field: "quote_eta", width: 120},
            {headerName: "Created At", field: "created_at", width: 120}
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
            isExternalFilterPresent: isExternalFilterPresent,
            doesExternalFilterPass: doesExternalFilterPass
        };

        function isExternalFilterPresent() {
            return self.extraFilters && self.extraFilters.dateRangeObj;
        }

        function doesExternalFilterPass(node) {
            var result = true;

            if(self.extraFilters.dateRangeObj && (moment(node.data.created_at + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.created_at + ' +0530') > self.extraFilters.dateRangeObj.endDate)){
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

        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            loadPartDocs();
        });

        self.externalFilterChanged = externalFilterChanged;
        self.loadPartDocs = loadPartDocs;
    })
;
