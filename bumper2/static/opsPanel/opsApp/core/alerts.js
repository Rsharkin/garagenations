angular.module('ops.views.alerts', [
    'ops.services.common'
])
    .controller('AlertsCtrl', function AlertsCtrl(CommonService, $scope){
        var self = this;

        self.extraFilters={};

        function loadAlerts(filters){
            if(filters == 'open'){
                filters = [{ 'op': 'ne', 'field': 'resolved', 'data': 1 }];
            }else{
                filters = '';
            }
            CommonService.getReportData('report_alerts_raised', filters)
                .then(function (data) {
                    if(data){
                        // console.log(data);
                        self.alerts = data.rows;
                        self.gridOptions.rowData = data.rows;
                        self.gridOptions.api.setRowData(data.rows);
                    }else{
                        sweetAlert("Oops...", "Failed to Load bookings", "error");
                    }
                });
        }

        loadAlerts('open');

        var render_resolved_col = function(params){
            if (params.data.resolved == 1){
                return '<span class="label label-default"> Resolved</span>';
            }else{
                return '<input ' +
                    'type="button" ' +
                    'class="btn btn-sm btn-primary" ' +
                    'value="Mark Resolved" ' +
                    'ng-click="alertsCtrl.markResolved('+params.data.id+')" />';
            }
        };

        var render_by_col = function(params){
            if (params.data.reason_type == 1){
                return '<span>Workshop</span>';
            }else if(params.data.reason_type == 2){
                return '<span>Crew</span>';
            }else{
                return '<span>'+params.data.reason_type+'</span>';
            }
        };

        var columnDefs = [
            {headerName: "Id", field: "id", filter: 'number'},
            {headerName: "Resolved", field: "resolved", cellRenderer:render_resolved_col},
            {headerName: "Workshop", field: "workshop_name"},
            {headerName: "Alert", field: "alert_reason", cellStyle: {'white-space': 'normal','overflow-y':'auto'}},
            {headerName: "Desc", field: "reason_text", cellStyle: {'white-space': 'normal','overflow-y':'auto'}},
            {headerName: "By", field: "reason_type", cellRenderer:render_by_col},
            {headerName: "Raised By", field: "raised_by", cellStyle: {'white-space': 'normal'}},
            {headerName: "Raised At", field: "raised_at", cellStyle: {'white-space': 'normal'}},
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
            doesExternalFilterPass: doesExternalFilterPass,
            onGridReady: function(event) {
                self.gridOptions.api.sizeColumnsToFit();
            }
        };

        function isExternalFilterPresent() {
            return self.extraFilters && self.extraFilters.dateRangeObj;
        }

        function doesExternalFilterPass(node) {
            var result = true;
            if(self.extraFilters.dateRangeObj && (moment(node.data.raised_at + ' +0530') < self.extraFilters.dateRangeObj.startDate || moment(node.data.raised_at + ' +0530') > self.extraFilters.dateRangeObj.endDate)){
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

        function markResolved(alertId){
            swal(
                {
                    title: "Mark Resolved?",
                    text: "Mark this issue resolved!!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Resolved!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    CommonService.markAlertResolved(alertId)
                        .then(function(response){
                            swal("Resolved!", "Issue has been marked resolved.", "success");
                            loadAlerts(self.removeResolved ? '':'open');
                            $scope.$emit('alertsUpdated','');
                        })
                    ;
                });
        }

        self.externalFilterChanged = externalFilterChanged;
        self.loadAlerts = loadAlerts;
        self.markResolved = markResolved;
    })
;
