/**
 * Created by Indy on 28/02/17.
 */
function SetLostReasonModalInstanceCtrl ($uibModalInstance, bookingId, BookingService, cancellationReasons, actionToSet) {
    var self = this;

    self.ajax_loading = false;
    self.item_list = cancellationReasons;
    self.bookingId = bookingId;

    self.ok = function () {
        self.ajax_loading = true;
        var selected_item_id = self.selected_item && self.selected_item.id != '?' ? self.selected_item.id:'';
        if(!selected_item_id){
            self.ajax_loading = false;
            sweetAlert("Error!", "Please select a Cancellation Reason.", "warning");
            return false;
        }
        var data = {
            'final_cancel_reason': selected_item_id
        };
        BookingService.saveBooking(bookingId, data, actionToSet)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Booking Marked LOST", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data;
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}