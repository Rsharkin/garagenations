/**
 * Created by Indy on 28/02/17.
 */
function FollowupModalInstanceCtrl ($uibModalInstance, bookingId, BookingService, CommonService, UserService,
                                    booking_caller, bookingCity) {
    var self = this;

    self.ajax_loading = false;
    self.modalItem = {
        'booking_id':bookingId
    };
    UserService.getOpsAgents().then(function(res){
        self.opsAgents = res;
    });
    CommonService.getMasterData(bookingCity).then(function(res){
        self.followupCommModes = res.followup_comm_modes;
        self.followupResults = res.followup_results;
    });
    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];
        var assigned_to = self.modalItem.assigned_to && self.modalItem.assigned_to.id != '?' ? self.modalItem.assigned_to.id: null;

        var data = {
            'followup': [{
                "note": self.modalItem.notes,
                "result": self.modalItem.result && self.modalItem.result.id != '?' ? self.modalItem.result.id: null,
                "comm_mode": self.modalItem.comm_mode
            }]
        };
        if(self.modalItem.result.action_type == 2 && assigned_to){
            data.assigned_to = assigned_to;
        }
        if(self.modalItem.result.action_type == 1 && moment(self.modalItem.nextFollowUpDt) < moment.now()){
            self.errorMsgs.push("Next Followup date should be greater than now.");
            self.ajax_loading = false;
            return false;
        }
        if(self.modalItem.result.action_type == 1 && self.modalItem.nextFollowUpDt){
            data.next_followup = self.modalItem.nextFollowUpDt;
        }
        BookingService.saveBookingFollowups(bookingId, data)
            .success(function(response){
                self.ajax_loading = false;
                if(!booking_caller){
                    // Save the current user as caller if booking is not assigned any caller.
                    var current_ops_user = UserService.getCurrentUser();
                    BookingService.saveBooking(bookingId,{'caller':current_ops_user.id}).then(function(response){
                        sweetAlert("success", "Followup Saved", "success");
                        $uibModalInstance.close('saved');
                    });
                }else{
                    sweetAlert("success", "Followup Saved", "success");
                    $uibModalInstance.close('saved');
                }

            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $uibModalInstance.rendered.then(function() {
        jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            orientation: 'auto'//,
            //minView: 1
        });
    });
}