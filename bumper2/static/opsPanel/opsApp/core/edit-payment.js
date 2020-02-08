/**
 * Created by Indy on 06/02/17.
 */
angular.module('ops.views.editPayment', [
    'ops.services.booking',
    'ops.services.common'
])
    .controller('EditPaymentCtrl', function EditPaymentCtrl($state, BookingService, CommonService){
        var self = this;

        self.booking = BookingService.getCurrentBooking();
        self.ajax_loading = false;
        self.editedPayment = {
            bookingId: self.booking.id,
            vendor_id: 'booking' + self.booking.id,
            source: 'opsPanel',
            tx_type: 1,
            status: 'success',
            tx_status: 1,
            used_credits: 0,
            vendor_tx_data: 'From Bumper ops panel'
        };

        CommonService.getMasterData(self.booking.city).then(function(data){
            delete data.payment_modes[5];
            self.paymentModes = data.payment_modes;
            console.log('self.paymentModes->', self.paymentModes);
            self.paymentVendors = data.payment_vendors;
        });

        function cancel(){
            $state.go('base.bookings.editBooking.billing', {bookingId:self.booking.id});
        }

        function savePayment(type){
            if(type != 1){
                self.editedPayment.tx_type = 2;
            }
            BookingService.addPayment(self.editedPayment).then(function(response){
                if(response.status == 200){
                    sweetAlert("success", "Payment Saved", "success");
                    $state.go('base.bookings.editBooking.billing', {bookingId:self.booking.id});
                }
            });
        }

        self.cancel = cancel;
        self.savePayment = savePayment;
    });