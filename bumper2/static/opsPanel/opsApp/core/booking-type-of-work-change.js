/**
 * Created by Indy on 28/02/17.
 */
function TypeOfWorkChangeModalInstanceCtrl ($uibModalInstance, bookingPackageId, userCarId, BookingService, panelId,
                                            bookingCity) {
    var self = this;

    self.ajax_loading = false;
    self.panel_list = null;
    self.showInternalPriceForm = false;
    self.selectedPanelPrice = null;

    BookingService.getPanelsByUserCarId(userCarId, null, bookingCity).then(function(res){
        for(var i=0; i< res.length; i++){
            var found = false;
            for(var j=0; j<res[i].price_list.length; j++){
                if(res[i].price_list[j].id == panelId){
                    found = true;
                    break;
                }
            }
            if(found){
                self.panelById=res[i];//panel extracted by panelId
                break;
            }
        }
    });

    self.ok = function (panel_item) {
        self.ajax_loading = true;

        if(!panel_item && self.selectedPanelPrice){
            panel_item = self.selectedPanelPrice;
        }
        var selected_panel_id = panel_item.id != '?' ? panel_item.id:'';
        if(!selected_panel_id){
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

        BookingService.updateTypeOfWork(bookingPackageId, selected_panel_id, self.internal_panel_price)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "type of work changed!!", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                self.errorMsg = 'Something went wrong on server.';

                if(response.non_field_errors){
                    self.errorMsg = 'This panel has already been added';
                }else{
                    self.errorMsg = 'error in changing type of work contact admin';
                }
                sweetAlert("Error", self.errorMsg, "error");
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}