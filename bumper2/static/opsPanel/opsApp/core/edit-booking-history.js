/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingHistory',[
    'ops.services.booking',
    'ops.services.common'
])
    .controller('EditBookingHistoryCtrl', function EditBookingHistoryCtrl($state, $scope, BookingService,
                                                                          CommonService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();

        function getHistoryForBooking(){
            var filters = [];
            filters.push({ 'op': 'eq', 'field': 'id', 'data': self.booking.id });
            CommonService.getReportData('report_booking_history', filters)
                .then(function (data) {
                    self.bookings = data.rows;
                    self.gridOptions.rowData = data.rows;
                    self.gridOptions.api.setRowData(data.rows);
                });
        }
        getHistoryForBooking();

        var render_status_col = function(params){
            return params.data.status;
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
        var render_location_col = function(params){
            var content = '';
            if(params.data.latitude && params.data.longitude){
                content = '<a href="http://maps.google.com/maps?t=m&q=loc:'+ params.data.latitude +'+'+ params.data.longitude +'" target="_blank" title="Map Location"><i class="fa fa-map-marker"></i></a>';
            }
            return content;
        };
        var columnDefs = [
            {headerName: "Updated Dt", field: "updated_at", width: 125},
            {headerName: "Updated By", field: "updated_by", width: 125},
            {headerName: "Location", field: "", width: 100,cellRenderer:render_location_col},
            {headerName: "Next FollowUp", field: "next_followup", width: 110},
            {headerName: "Status", field: "status_id", width: 150,cellRenderer:render_status_col, filter: ''},
            {headerName: "Ops Status", field: "ops_status", width: 150},
            {headerName: "Assigned To", field: "assigned_to", width: 150},
            {headerName: "Created Dt", field: "created_at", width: 85},
            {headerName: "Comments", field: "desc", width: 200},
            {headerName: "Car", field: "model", width: 125,cellRenderer:render_car_col},
            {headerName: "Source", field: "source", width: 125},
            {headerName: "Workshop ETA", field: "workshop_eta"},
            {headerName: "Customer ETA", field: "cust_eta"},
            {headerName: "Pickup Time", field: "p_time", cellRenderer:render_pickup_time_col, width: 250},
            {headerName: "Actual Pickup Time", field: "e_p_time"},
            {headerName: "Drop Time", field: "d_time", cellRenderer:render_end_time_col, width: 250},
            {headerName: "Delivered At", field: "e_d_time"},
            {headerName: "Workshop", field: "workshop"}
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
            suppressCellSelection:true
        };
    });