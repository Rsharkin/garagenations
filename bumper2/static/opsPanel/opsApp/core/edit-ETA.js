/**
 * Created by Indy on 07/02/17.
 */
function SetETAModalInstanceCtrl($uibModalInstance, BookingService, booking, is_daily_update, CommonService) {
    var self = this,
        data = {
            'estimate_complete_time': booking.estimate_complete_time,
            'workshop_eta': booking.workshop_eta
        };

    self.ajax_loading = false;
    self.booking = booking;
    self.old_estimate_complete_time = booking.estimate_complete_time;
    self.captureDelayReason = false;

    CommonService.getMasterData(self.booking.city).then(function(res){
        self.delayReasons = res.delay_reasons;
    });

    function etaChanged(){
        self.captureDelayReason = false;
        /* if customer eta was there and now changed. */
        if(data.estimate_complete_time && (data.estimate_complete_time !== self.booking.estimate_complete_time)){
            self.captureDelayReason = true;
        }
        /* if workshop eta was there and now changed. */
        if(data.workshop_eta && (data.workshop_eta !== self.booking.workshop_eta)){
            self.captureDelayReason = true;
        }
    }

    self.ok = function () {
        self.errorMsgs = [];
        self.ajax_loading = true;

        data = {
            'estimate_complete_time': booking.estimate_complete_time,
            'workshop_eta': booking.workshop_eta
        };

        if(self.captureDelayReason && !self.booking.delay_reason){
            self.errorMsgs.push("Delay Reason is required.");
            self.ajax_loading = false;
            return false;
        }

        if(self.captureDelayReason && self.booking.delay_reason.id === 14 && !self.booking.reason_text){
            self.errorMsgs.push("Delay Details is required.");
            self.ajax_loading = false;
            return false;
        }

        if(self.captureDelayReason){
            if(self.booking.reason_text){
                data.reason_text = self.booking.reason_text;
            }
            data.delay_reason = self.booking.delay_reason && self.booking.delay_reason.id != '?' ? self.booking.delay_reason.id: null;
        }

        if(!data.estimate_complete_time || !data.workshop_eta){
            self.errorMsgs.push("Please select both Workshop and Customer ETA.");
            self.ajax_loading = false;
            return false;
        }
        if(moment(data.estimate_complete_time) < moment(data.workshop_eta).add(3, 'hour')){
            self.errorMsgs.push("Customer ETA must be 3 hours greater than workshop ETA.");
            self.ajax_loading = false;
            return false;
        }
        if(moment(data.estimate_complete_time) < moment.now() || moment(data.workshop_eta) < moment.now()){
            self.errorMsgs.push("ETA cannot be less than current time.");
            self.ajax_loading = false;
            return false;
        }

        BookingService.saveBooking(booking.id, data)
            .success(function(response){
                // if(is_daily_update){
                //     var change_entity_data = {
                //         'content_type': 1,
                //         'content_id': booking.id,
                //         'item_tracked': 'estimate_complete_time',
                //         'change_type': self.old_estimate_complete_time == data.estimate_complete_time? 1:2,
                //         'old_value': data.estimate_complete_time,
                //         'new_value': data.estimate_complete_time
                //     };
                //     CommonService.updateEntityChange(change_entity_data)
                //         .success(function(response){
                //             self.ajax_loading = false;
                //             sweetAlert("success", "ETA Updated", "success");
                //             $uibModalInstance.close('saved');
                //         });
                // }else{
                //     self.ajax_loading = false;
                //     sweetAlert("success", "ETA Updated", "success");
                //     $uibModalInstance.close('saved');
                // }
                self.ajax_loading = false;
                sweetAlert("success", "ETA Updated", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsgs.push('Please make sure all values are correctly filled: ' + response.data);
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $uibModalInstance.rendered.then(function() {
        jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:00",
            autoclose: true,
            //todayBtn: true,
            startDate: "2015-07-01 10:00",
            //minuteStep: 5,
            orientation: 'auto',
            minView: 1
            // showMeridian: true
        });
    });

    self.etaChanged = etaChanged;
}
