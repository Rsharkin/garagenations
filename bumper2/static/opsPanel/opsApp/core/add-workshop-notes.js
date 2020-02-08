/**
 * Created by Indy on 28/02/17.
 */
function WorkshopNotesModalInstanceCtrl ($uibModalInstance, bookingId, BookingService, CommonService, bookingCity,
                                         purpose) {
    var self = this;

    self.ajax_loading = false;
    self.purpose = purpose;
    self.modalItem = {
        'booking_id':bookingId
    };

    CommonService.getMasterData(bookingCity).then(function(res){
        self.followupCommModes = res.followup_comm_modes;
        self.followupResults = res.followup_results;
    });

    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];

        var note = self.modalItem.notes;
        if(self.purpose === 'reason_allow_to_go_failed_qc'){
            note = 'REASON TO ALLOW DELIVERY AFTER CREW QC FAIL:: ' + note;
        }

        var data = {
            'followup': [{
                "note": note,
                "result": self.modalItem.result && self.modalItem.result.id != '?' ? self.modalItem.result.id: null,
                "comm_mode": self.modalItem.comm_mode,
                "follow_for": 2
            }]
        };
        BookingService.saveBookingFollowups(bookingId, data)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Workshop Note Saved", "success");
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
}