/**
 * Created by Indy on 28/02/17.
 */
function SendEODModalInstanceCtrl($uibModalInstance, BookingService, booking, is_daily_update, CommonService) {
    var self = this;

    self.ajax_loading = false;
    self.booking = booking;
    self.errorMsgs = [];
    self.subErrorMsgs = [];
    self.action_based_on_status = null;
    self.add_message_manually = false;
    self.manual_eod = false;
    self.CommModes = {
        1: 'SMS',
        2: 'PUSH',
        3: 'EMAIL'
    };

    BookingService.getEODMessage(booking.id).success(function (response) {
        if(response.message){
            self.errorMsgs.push(response.message);
            self.add_message_manually = true;
        }else{
            self.messagesToSend = response.data;
            self.action_based_on_status = response.action_based_on_status;
        }
    });

    self.ok = function () {
        self.errorMsgs = [];
        self.ajax_loading = true;

        var data = {
            'action': self.action_based_on_status
        };

        BookingService.sendEODMessage(booking.id, data)
            .success(function(response){
                if(is_daily_update){
                    var change_entity_data = {
                        'content_type': 1,
                        'content_id': booking.id,
                        'item_tracked': 'eod_message',
                        'change_type': 2
                    };

                    CommonService.updateEntityChange(change_entity_data)
                        .success(function(response){
                            self.ajax_loading = false;
                            sweetAlert("success", "Message Sent", "success");
                            $uibModalInstance.close('saved');
                        });
                }else{
                    self.ajax_loading = false;
                    sweetAlert("success", "Message Sent", "success");
                    $uibModalInstance.close('saved');
                }
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

    self.saveManualEOD = function () {
        self.subErrorMsgs = [];
        self.ajax_loading = true;

        if(!self.manual_eod.message){
            self.subErrorMsgs.push('Please enter message that was sent.');
            self.ajax_loading = false;
            return false;
        }
        if(!self.manual_eod.message_type){
            self.subErrorMsgs.push('Please select communication mode.');
            self.ajax_loading = false;
            return false;
        }

        BookingService.saveManualEODMessage(booking.id, self.manual_eod)
            .success(function(response){
                if(is_daily_update){
                    var change_entity_data = {
                        'content_type': 1,
                        'content_id': booking.id,
                        'item_tracked': 'eod_message',
                        'change_type': 2,
                        'old_value': 'manual_entry'
                    };

                    CommonService.updateEntityChange(change_entity_data)
                        .success(function(response){
                            self.ajax_loading = false;
                            sweetAlert("success", "Message Sent", "success");
                            $uibModalInstance.close('saved');
                        });
                }else{
                    self.ajax_loading = false;
                    sweetAlert("success", "Message Sent", "success");
                    $uibModalInstance.close('saved');
                }
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.subErrorMsgs.push('Please make sure all values are correctly filled: ' + response.data);
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}