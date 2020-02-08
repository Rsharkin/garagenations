/**
 * Created by Indy on 28/02/17.
 */
function RescheduleDropModalInstanceCtrl($uibModalInstance, BookingService, booking) {
    var self = this;
    self.errorMsgs = [];
    self.newTime = {
        "start":null,
        "end" :null
    };

    function updatePickupTime(){
        var actionToSet = 19;
        self.pickUpData = {
            'drop_time':self.newTime.start,
            'drop_slot_end_time':self.newTime.end
        };

        if(self.newTime.end < self.newTime.start){
            self.errorMsgs.push("End time should not be less start time.");
            return false;
        }
        self.ajax_loading = true;

        BookingService.saveBooking(booking.id,self.pickUpData, actionToSet)
            .success(function (response){
                self.ajax_loading = false;
                $uibModalInstance.close('saved');
                sweetAlert("success", "Booking Updated", "success");
            })
            .error(function(response){
                self.ajax_loading = false;
                self.errorMsg = 'Something went wrong on server.';
                if(response.non_field_errors){
                    self.errorMsg = response.non_field_errors[0];
                }else{
                    self.errorMsg = 'Please make sure all values are correctly filled.';
                }
                sweetAlert("Error", self.errorMsg, "error");
            });
    }
    self.cancel = function () {
        $uibModalInstance.close('cancel');
    };

    $uibModalInstance.rendered.then(function() {
        jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            orientation: 'auto'//,
            //minView: 1
        });
    });

    self.updatePickupTime = updatePickupTime;
}