/**
 * Created by Indy on 28/02/17.
 */
function RescheduleModalInstanceCtrl($uibModalInstance,BookingService,booking) {
    var self = this;
    self.newTime = {
        "start":null,
        "end" :null
    };

    function updatePickupTime(){
        var actionToSet = 3;
        if(booking.is_doorstep === true){
            actionToSet = 26;
        }
        self.pickUpData = {
            'pickup_time':self.newTime.start,
            'pickup_slot_end_time':self.newTime.end
        };
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

    function followupOps(){
        var actionToSet = 108;
        if(booking.is_doorstep === true){
            actionToSet = 111;
        }
        BookingService.saveBooking(booking.id,{},actionToSet).then(function(response){
            $uibModalInstance.close('saved');
            swal("Done!", "Ops Status Set to Following-Up.", "success");
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
    self.followupOps = followupOps;
}