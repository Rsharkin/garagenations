/**
 * Created by Indy on 28/02/17.
 */
function AssignWorkshopModalInstanceCtrl($uibModalInstance, bookingId, BookingService, CommonService, bookingCity) {
    var self = this;

    self.ajax_loading = false;
    //self.item_list = DataService.masterData.workshops;
    self.bookingId = bookingId;

    CommonService.getMasterData(bookingCity).then(function(res){
        self.item_list = res.workshops;
    });

    self.ok = function () {
        self.ajax_loading = true;
        var selected_item_id = self.selected_item && self.selected_item.id != '?' ? self.selected_item.id:'';
        if(!selected_item_id){
            self.ajax_loading = false;
            sweetAlert("Error!", "Please select a Workshop.", "warning");
            return false;
        }
        var data = {
            'workshop': selected_item_id
        };

        BookingService.saveBooking(bookingId, data)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Workshop Assigned", "success");
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