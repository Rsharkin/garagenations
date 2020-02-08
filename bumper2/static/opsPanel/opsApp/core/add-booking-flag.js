/**
 * Created by Indy on 01/05/17.
 */
function AddBookingFlagModalCtrl ($uibModalInstance, BookingService, bookingId , bookingFlags) {
    var self = this;

    self.ajax_loading = false;
    self.bookingFlags = bookingFlags;

    self.modalItem = {
        'booking':bookingId,
        'flag_type':1,
        'reason':null
    };

    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];

        BookingService.addBookingFlag(self.modalItem)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Flag Added", "success");
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
                    sweetAlert("Error", "Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}