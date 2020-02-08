/**
 * Created by Indy on 28/02/17.
 */
function AddReworkPanelModalInstanceCtrl ($uibModalInstance, BookingService, bookingPackagePanel, CommonService,
                                          bookingCity) {
    var self = this;
    self.ajax_loading = false;
    self.bookingPackagePanel = bookingPackagePanel;
    self.rework = {
        'booking_package_panel': bookingPackagePanel.id
    };

    CommonService.getMasterData(bookingCity).then(function(res){
        delete res.type_of_works['9'];
        self.typeOfWorks = res.type_of_works;
    });

    self.ok = function () {
        self.ajax_loading = true;

        BookingService.addReworkPanelToBooking(self.rework)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Rework Panel Added", "success");
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