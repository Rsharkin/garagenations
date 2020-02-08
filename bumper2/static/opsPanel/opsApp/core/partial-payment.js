/**
 * Created by rishisharma on 23/03/17.
 */
/**
 * Created by Indy on 28/02/17.
 */
function PartialPaymentModalInstanceCtrl($uibModalInstance, BookingService, booking) {
    var self = this;

    self.ajax_loading = false;
    self.booking = booking;
    self.errorMsgs = [];
    self.modalItem = {
        'booking': booking.id,
        'status': 1
    };
    self.ok = function () {
        if(!self.booking.payment_details.pending_payment_id){
            //initiating payment if not id
            var result = BookingService.initiatePayment(self.booking.id, {payment_type: 2});
            result.success(function (result) {
                $scope.$emit('bookingChanged','');
            }).error(function () {
                sweetAlert("Error in initiating payment", "contact admin");
            });
        }
        self.errorMsgs = [];
        self.ajax_loading = true;
        // price ot be set = self.modalItem.payable_amt
        // expiry time to set
        var currentDate = new Date();
        var expiryTime = currentDate.setHours(currentDate.getHours()+6);
        var res = BookingService.generatePaymentLink(self.booking.id);
        res.success(function (result) {
            self.ajax_loading = false;
            sweetAlert("Link for direct payment:", "CONFIG_BASE_URL"+"direct-payment/?pid="+result.token+"&a="+self.modalItem.payable_amt+"&t="+expiryTime);
        }).error(function () {
            sweetAlert("Error in initiating payment link", "contact admin");
        });
    };
    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}