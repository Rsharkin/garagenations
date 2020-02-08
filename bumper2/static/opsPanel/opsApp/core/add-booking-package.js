/**
 * Created by Indy on 15/02/17.
 */
function AddPackageModalInstanceCtrl($uibModalInstance, BookingService, bookingId, usercarId, isExtra,
                                     existingPackagePriceList, bookingCity) {
    var self = this;

    self.ajax_loading = false;
    self.package_list = null;
    BookingService.getPackages(usercarId, bookingCity).then(function(res){
        var list_to_show = [];
        for(var i=0; i< res.length; i++){
            var found = false;
            for(var j=0; j<existingPackagePriceList.length; j++){
                if(existingPackagePriceList[j].id == res[i].id){
                    found = true;
                    break;
                }
            }
            if(!found){
                list_to_show.push(res[i]);
            }
        }
        self.package_list = list_to_show;
    });

    self.ok = function () {
        self.ajax_loading = true;

        var selectedPackId = self.selected_package && self.selected_package.id != '?' ? self.selected_package.id:'';
        if(!selectedPackId){
            self.ajax_loading = false;
            sweetAlert("Error!", "Please select some package.", "warning");
            return false;
        }
        if(self.selected_package.package.internal && !self.internal_package_price){
            self.ajax_loading = false;
            sweetAlert("Error!", "Since this is internal package, Please provide the price.", "warning");
            return false;
        }

        BookingService.addPackageToBooking(bookingId, selectedPackId, self.internal_package_price, isExtra)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Package Added", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                if(Object.prototype.toString.call( response ) === '[object Array]' ){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response;
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}