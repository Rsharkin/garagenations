/**
 * Created by Indy on 28/02/17.
 */
function ProformaInvoiceModalInstanceCtrl($uibModalInstance, BookingService, booking) {
    var self = this;

    self.ajax_loading = false;
    self.booking = booking;
    self.errorMsgs = [];
    self.modalItem = {
        'booking': booking.id,
        'status': 1
    };

    self.ok = function () {
        self.errorMsgs = [];
        self.ajax_loading = true;

        BookingService.generateProformaInvoice(self.modalItem)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Proforma Invoice Generated", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsgs.push('Please make sure all values are correctly filled: ' + response.data);
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}