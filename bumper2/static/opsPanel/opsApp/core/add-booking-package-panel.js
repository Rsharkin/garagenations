/**
 * Created by Indy on 15/02/17.
 */
function AddPanelToPackageModalInstanceCtrl ($uibModalInstance, BookingService, bookingPackageId, userCarId,
                                             existingPanelList, existingPackages, isExtra, bookingCity) {
    var self = this;

    self.ajax_loading = false;
    self.panel_list = null;
    self.showInternalPriceForm = false;
    self.selectedPanelPrice = null;
    self.fullbodySelected = false;
    for (var i=0; i<existingPackages.length;i++){
        if (existingPackages[i].package.category==3){
            self.fullbodySelected = true;
            break;
        }
    }
    BookingService.getPanelsByUserCarId(userCarId, self.fullbodySelected, bookingCity).then(function (res) {
        var list_to_show = [];
        for (var i = 0; i < res.length; i++) {
            var found = false;
            for (var j = 0; j < existingPanelList.length; j++) {
                if (existingPanelList[j] == res[i].price_list[0].panel_id) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                list_to_show.push(res[i]);
            }
        }
        self.panel_list = list_to_show;
    });
    self.ok = function (panel_item) {
        self.ajax_loading = true;

        if(!panel_item && self.selectedPanelPrice){
            panel_item = self.selectedPanelPrice;
        }
        var selectedPanelId = panel_item.id != '?' ? panel_item.id:'';
        if(!selectedPanelId){
            self.ajax_loading = false;
            sweetAlert("Error!", "Please select some panel.", "warning");
            return false;
        }
        if(panel_item.internal && !self.internal_panel_price){
            self.ajax_loading = false;
            self.showInternalPriceForm = true;
            self.selectedPanelPrice = panel_item;
            //sweetAlert("Error!", "Since this is internal panel, Please provide the price.", "warning");
            return false;
        }

        BookingService.addPanelToPackage(bookingPackageId, selectedPanelId, self.internal_panel_price, isExtra)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Panel Added", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response, status_code){
                self.ajax_loading = false;
                self.errorMsg = 'Something went wrong on server.';

                // console.log(response, status_code);
                if(status_code === 400){
                    if(response.detail){
                        self.errorMsg = response.detail;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                }
                sweetAlert("Error", self.errorMsg, "error");
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}