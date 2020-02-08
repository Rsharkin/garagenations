/**
 * Created by Indy on 28/02/17.
 */
function AssignWorkshopManagersModalInstanceCtrl($uibModalInstance, BookingService, UserService, bookingId,
                                                 whoToAssign) {
    var self = this;

    self.ajax_loading = false;
    self.item_list = null;
    self.bookingId = bookingId;
    self.selectedItem = null;

    if(whoToAssign === 'WorkshopAssistantManager'){
        UserService.getUsersByRole('WorkshopAssistantManager').then(function(res){
            self.item_list = res;
        });
    }else if(whoToAssign === 'WorkshopManager'){
        UserService.getUsersByRole('WorkshopManager').then(function(res){
            self.item_list = res;
        });
    }


    self.ok = function () {
        self.ajax_loading = true;

        var data = {};
        if(whoToAssign === 'WorkshopAssistantManager'){
            data = {'workshop_asst_mgr': self.selectedItem};
        }else if(whoToAssign === 'WorkshopManager'){
            data = {'workshop_manager': self.selectedItem};
        }

        BookingService.saveBooking(bookingId, data)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Assignment Done", "success");
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