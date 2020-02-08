/**
 * Created by Indy on 21/02/17.
 */
function ReturnCarModalInstanceCtrl($uibModalInstance, BookingService, booking, CommonService) {
    var self = this;
    self.ajax_loading = false;
    self.booking = booking;
    self.isProformaInvoiceCreated = false;
    self.isProformaInvoicePending = false;
    self.isProformaInvoicePaid = false;
    self.needToCollectAnyAmount = false;

    CommonService.getMasterData(self.booking.city).then(function(data){
        self.returnReasons = data.return_reasons;
    });

    BookingService.getBookingBill(self.booking.id).then(function (result) {
        if(result.data) {
            self.bookingBill = result.data;

            self.isProformaInvoiceCreated = self.bookingBill.bill_details.proforma_invoices.length > 0;
            if(self.isProformaInvoiceCreated){
                self.isProformaInvoicePending = _.some(self.bookingBill.bill_details.proforma_invoices,
                    function(o){if(o.status===1){return true;} });

                self.isProformaInvoicePaid = _.some(self.bookingBill.bill_details.proforma_invoices,
                    function(o){if(o.status===3){return true;} });
            }
        }
    });

    function scheduleDrop(){
        self.ajax_loading = true;
        var actionToSet = 147; // drop schedule pending
        if(self.needToCollectAnyAmount == 1){
            actionToSet = 16; // pending payment and drop schedule pending.
        }

        if(!self.isProformaInvoicePaid && self.isProformaInvoicePending){
            // cancel the pending payment invoice.
            var pendingInvoice = _.find(self.bookingBill.bill_details.proforma_invoices, {'status': 1});
            if(pendingInvoice){
                BookingService.cancelProformaInvoice(pendingInvoice.id);
            }
        }

        var data = {
            return_reason: self.selectedReasonForReturn && self.selectedReasonForReturn.id != '?' ? self.selectedReasonForReturn.id:'',
            return_wo_work: true
        };

        BookingService.saveBooking(booking.id, data, actionToSet).then(function(response){
            self.ajax_loading = false;
            $uibModalInstance.close('saved');
            swal("Done!", "Booking set to drop schedule pending.", "success");
        });
    }

    self.cancel = function () {
        $uibModalInstance.close('cancel');
    };
    self.scheduleDrop = scheduleDrop;
}