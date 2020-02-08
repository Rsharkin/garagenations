/*jshint -W018 */
angular.module('ops.views.notifyUsers', [
    'ops.services.common'
])
    .controller('NotifyUsersCtrl', function NotifyUsersCtrl(CommonService){
        var notifyUsersCtrl = this;
        notifyUsersCtrl.notice = {};

        CommonService.getReportData('report_notify_user')
            .then(function (data) {
                if(data){
                    notifyUsersCtrl.gridOptions.rowData = data.rows;
                    notifyUsersCtrl.gridOptions.api.setRowData(data.rows);
                }else{
                    sweetAlert("Oops...", "Failed to Users", "error");
                }
            });

        var render_is_otp_validated_col = function(params){
            var html = '<p class="text-center"><img src="/static/admin/img/icon-yes.gif" alt="True"></p>';
            if(!params.data.is_otp_validated){
                html = '<p class="text-center"><img src="/static/admin/img/icon-no.gif" alt="True"></p>';
            }
            return html;
        };

        var render_web_lead_col = function(params){
            //console.log(params.data.web_lead);
            var html = '<p class="text-center"><img src="/static/admin/img/icon-no.gif" alt="True"></p>';
            if(params.data.web_lead){
                html = '<p class="text-center"><img src="/static/admin/img/icon-yes.gif" alt="True"></p><p>' + params.data.lead_create_at + '</p>';
            }
            return html;
        };

        var render_app_install_col = function(params){
            var html = '<p class="text-center"><img src="/static/admin/img/icon-yes.gif" alt="True"></p>';
            if(!params.data.app_install){
                html = '<p class="text-center"><img src="/static/admin/img/icon-no.gif" alt="True"></p>';
            }
            return html;
        };

        var render_car_col = function(params){
            if(params.data.car){return '<p class="text-center">' + params.data.car + '</p> <p class="text-center">' + params.data.car_fuel_type + '</p>';}else{ return '';}
        };

        var render_bookings_col = function(params){
            var items = params.data.latest_booking? params.data.latest_booking.split(','):'';
            if(items){
                return '<a ui-sref="base.editBooking({bookingId:'+items[0]+'})" target="_blank">[ID:'+ items[0] +'] ' + items[1] + '</a><br> ';
            }else{
                return '';
            }
        };

        var columnDefs = [
            {headerName: "", field: "selected", width: 58,checkboxSelection:true},
            {headerName: "OTP", field: "is_otp_validated", width: 58,cellRenderer:render_is_otp_validated_col},
            {headerName: "Name", field: "name", width: 150},
            {headerName: "Phone", field: "phone", width: 100},
            {headerName: "Email", field: "email", width: 200},
            {headerName: "City", field: "city", width: 85},
            {headerName: "Car", field: "car", width: 85,cellRenderer:render_car_col},
            {headerName: "# Bookings", field: "bookings", cellClass:'text-center'},
            {headerName: "Latest Booking", field: "latest_booking",cellRenderer:render_bookings_col},
            {headerName: "Date Joined", field: "date_joined"}

        ];

        notifyUsersCtrl.gridOptions = {
            columnDefs: columnDefs,
            rowData: null,
            // rowSelection: 'multiple',
            rowHeight: 75,
            enableColResize: true,
            enableSorting: true,
            suppressMultiSort: true,
            enableFilter: true,
            angularCompileRows: true,
            suppressRowClickSelection:true,
            suppressCellSelection:true,
            selectionChanged: selectionChangedFunc
        };

        function selectionChangedFunc() {
            notifyUsersCtrl.selected_rows_length = notifyUsersCtrl.gridOptions.api.getSelectedNodes().length;
        }

        function deselect_all(){
            notifyUsersCtrl.gridOptions.api.deselectAll();
        }


        function sendNotification(){
            notifyUsersCtrl.ajax_loading = true;

            notifyUsersCtrl.notice.notice_type = notifyUsersCtrl.notice.type != '?' ? notifyUsersCtrl.notice.type:'';
            notifyUsersCtrl.notice.label = notifyUsersCtrl.notice.label != '?' ? notifyUsersCtrl.notice.label:'';

            if(!notifyUsersCtrl.notice.notice_type || !notifyUsersCtrl.notice.label){
                notifyUsersCtrl.ajax_loading = false;
                sweetAlert("Error", "Please select Type/ Label for notification.", "warning");
                return false;
            }
            var selected_nodes = notifyUsersCtrl.gridOptions.api.getSelectedNodes();

            if(!selected_nodes.length > 0){
                notifyUsersCtrl.ajax_loading = false;
                sweetAlert("Error", "Please select Some users", "warning");
                return false;
            }else if(selected_nodes.length > 1){
                notifyUsersCtrl.ajax_loading = false;
                sweetAlert("Error, Notification can be sent to only one customer.", "Please de-select other customers", "warning");
                return false;
            }

            var user_ids = [];

            for(var i=0; i<selected_nodes.length;i++){
                user_ids.push(selected_nodes[i].data.id);
            }

            notifyUsersCtrl.notice.user_ids = user_ids.join(',');

            CommonService.notifyUser(notifyUsersCtrl.notice)
                .success(function(res){
                    notifyUsersCtrl.ajax_loading = false;
                    sweetAlert("Message Sent", '', "success");
                })
                .error(function(response){
                    notifyUsersCtrl.ajax_loading = false;
                    notifyUsersCtrl.errorMsg = 'Something went wrong on server.';

                    if(response.non_field_errors){
                        notifyUsersCtrl.errorMsg = response.non_field_errors[0];
                    }else{
                        notifyUsersCtrl.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", notifyUsersCtrl.errorMsg, "error");
                });
        }

        notifyUsersCtrl.deselect_all = deselect_all;
        notifyUsersCtrl.sendNotification = sendNotification;

    })
;

