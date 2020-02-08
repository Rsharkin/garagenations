/**
 * Created by rishisharma on 09/04/17.
 */
function CallNotesModalController ($scope,$uibModalInstance, bookingId, BookingService, CommonService, UserService,
                                   bookingCity) {
    var self = this;

    self.ajax_loading = false;
    self.modalItem = {
        'booking_id':bookingId
    };
    UserService.getOpsAgents().then(function(res){
        self.opsAgents = res;
    });
    CommonService.getMasterData(bookingCity).then(function(res){
        self.followupResults = res.followup_results;
    });

    var callInitiateData = {
        'followup': [{
            "note": "Initiated call",
            "result": null,
            "comm_mode": "1"
        }]
    };
    BookingService.saveBookingFollowups(bookingId,callInitiateData)
        .success(function(response){
            //initial follow up saved
        })
        .error(function(response){
            //follow up not saved
        });

    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];
        var assigned_to = self.modalItem.assigned_to && self.modalItem.assigned_to.id != '?' ? self.modalItem.assigned_to.id: null;

        var data = {
            'followup': [{
                "note": self.modalItem.notes,
                "result": self.modalItem.result && self.modalItem.result.id != '?' ? self.modalItem.result.id: null,
                "comm_mode": "1"
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
                sweetAlert("success", "Followup Saved", "success");
                $uibModalInstance.close('saved');
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