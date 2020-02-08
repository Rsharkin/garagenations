/**
 * Created by Indy on 28/02/17.
 */
function AddReworkPackageModalInstanceCtrl ($uibModalInstance, BookingService, bookingPackage) {
    var self = this;
    self.ajax_loading = false;
    self.bookingPackage = bookingPackage;
    self.rework = {
        'booking_package': bookingPackage.id
    };

    self.ok = function () {
        self.ajax_loading = true;

        BookingService.addReworkPackageToBooking(self.rework)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Rework Package Added", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.errorMsg = 'Something went wrong on server.';
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    self.errorMsg =  "You don't have permission required to do this action.";
                }else if(status == '400'){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data;
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}
