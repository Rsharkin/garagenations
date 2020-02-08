/**
 * Created by Indy on 28/02/17.
 */
function AssignDriverModalInstanceCtrl ($uibModalInstance, bookingId, BookingService, UserService, driver_for,
                                        actionToSet, assignmentFor) {
    // Here driver_for means [pickup/drop]
    // Here assignmentFor means [team/driver]
    var self = this;

    self.ajax_loading = false;
    self.item_list = null;
    self.driver_for = driver_for;
    self.bookingId = bookingId;
    self.assignmentFor = assignmentFor && assignmentFor === 'Team'? "Team Incharge" : driver_for + ' Driver';

    UserService.getActiveDrivers().then(function(res){
        self.item_list = res;
    });

    self.ok = function () {
        self.ajax_loading = true;

        var selected_driver_id = self.selected_item && self.selected_item.id != '?' ? self.selected_item.id:'';
        if(!selected_driver_id){
            self.ajax_loading = false;
            sweetAlert("Error!", "Please select a driver.", "warning");
            return false;
        }
        var data = {};
        if(driver_for == 'Pickup'){
            data = {'pickup_driver': selected_driver_id};
        }else if(driver_for == 'Drop'){
            data = {'drop_driver': selected_driver_id};
        }
        BookingService.saveBooking(bookingId, data, actionToSet)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Driver assigned", "success");
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