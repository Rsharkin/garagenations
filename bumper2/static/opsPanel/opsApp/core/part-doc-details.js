/**
 * Created by Indy on 21/07/17.
 */
angular.module('ops.views.partDocDetails',[
    'ops.services.booking',
    'ops.services.common'
]).controller('PartDocDetailsCtrl', function($scope, $stateParams, BookingService, CommonService){
    var self = this;

    self.editedPartDoc = null;
    self.bookingData = null;
    self.userCar = null;
    self.ajax_loading = false;
    self.partDocId = $stateParams.partDocId;
    self.bookingId = $stateParams.bookingId;
    self.partVendors = null;
    self.selectedQuoteExpired = false;
    self.selectedQuote = null;

    BookingService.getBookingById(self.bookingId).then(function (data) {
        self.bookingData = data;
        CommonService.getUserCar(self.bookingData.usercar)
            .then(function (data) {
                self.userCar = data;
            });
    });

    BookingService.getPartVendors().then(function (data) {
        self.partVendors = data;
    });

    function loadData(){
        BookingService.getPurchaseRequisitionTerm(self.partDocId).then(function (data) {
            self.editedPartDoc = data;
            setTimeout(function(){
                loadDatePlugin();
            }, 1000);
        });
    }

    function loadQuotes(){
        BookingService.getPartQuote(self.partDocId).then(function (data) {
            self.quotes = data;
            for(var i=0; i< self.quotes.length; i++){
                if(self.quotes[i].selected === true && (moment() > moment(self.quotes[i].created_at).utcOffset('+0530')) ){
                    self.selectedQuoteExpired = true;
                    self.selectedQuote = self.quotes[i];
                    break;
                }
            }
        });
    }

    loadData();
    loadQuotes();

    function saveNotes(){
        self.ajax_loading = true;
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {'notes':[self.newNote]})
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Note added", "success");
                self.addNote=false;
                self.newNote.note='';
                loadData();
            });
    }

    function markWillGetQuote(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {'status': 2})
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Status updated", "success");
                loadData();
            });
    }

    function markOrderPlaced(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {'status': 8})
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Order Placed Updated.", "success");
                loadData();
            });
    }

    function markInTransit(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {'status': 9})
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "In Transit Updated.", "success");
                loadData();
            });
    }

    function markPartReceived(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {
            'status': 10,
            'part_number': self.editedPartDoc.part_number,
            'net_dealer_price': self.editedPartDoc.net_dealer_price,
            'mrp': self.editedPartDoc.mrp

        })
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Part Received Updated.", "success");
                loadData();
            });
    }

    function markRequestDeclined(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {
            'status': 3,
            'quote_eta_reason':self.editedPartDoc.quote_eta_reason
        })
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Status updated", "success");
                loadData();
            });
    }

    function markQuoteToBeExpectedBy(){
        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {
            'status': 4,
            'quote_eta_reason':self.editedPartDoc.quote_eta_reason,
            'quote_eta': self.editedPartDoc.quote_eta
        })
            .then(function () {
                self.ajax_loading = false;
                sweetAlert("success", "Status updated", "success");
                loadData();
            });
    }

    function addQuote() {
        self.ajax_loading = true;
        var data = {
            "booking_part_doc": self.partDocId,
            "status":1,
            "part_number": self.newQuote.part_number,
            "price": self.newQuote.price,
            "eta": self.newQuote.eta,
            "quote_type": self.newQuote.quote_type,
            "vendor": self.newQuote.vendor
        };
        if(self.newQuote.notes){
            data.notes = [{"note": self.newQuote.notes}];
        }
        BookingService.addPartQuote(data)
            .success(function(response){
                self.ajax_loading = false;
                self.showAddQuote = false;
                self.newQuote = {};
                sweetAlert("success", "Quote saved", "success");
                loadQuotes();
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    }

    function markQuoteSelected(quoteId){
        swal(
            {
                title: "Select this Quote?",
                text: "After selection part price will be updated and shown to customer. After this no more quote can be added and this quote cannot be changed.",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Select This Quote!",
                showLoaderOnConfirm: true,
                closeOnConfirm: true
            },
            function(){
                self.ajax_loading = true;
                BookingService.updatePartQuote(quoteId, {'selected': 1})
                    .success(function(response){
                        BookingService.updatePurchaseRequisitionTerm(self.partDocId, {'status': 5})
                            .then(function () {
                                self.ajax_loading = false;
                                sweetAlert("success", "Quote Selected and price will be shown to customer.", "success");
                                loadData();
                                loadQuotes();
                            });
                    })
                    .error(function(response){
                        self.ajax_loading = false;
                        var status = response.status;
                        if(status == '401'){
                            sweetAlert("Error", "You don't have permission required to do this action.", "error");
                        }else if(status == '400'){
                            self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                        }else{
                            sweetAlert("Error", "Errors: Server Error", "error");
                        }
                    });
            });
    }


    function deleteQuote(quoteId){
        self.ajax_loading = true;
        BookingService.deletePartQuote(quoteId)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Quote Deleted.", "success");
                loadQuotes();
            })
            .error(function(response){
                self.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Error", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                }else{
                    sweetAlert("Error", "Errors: Server Error", "error");
                }
            });
    }

    function loadDatePlugin(){
        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });

    }
    loadDatePlugin();

    self.saveNotes = saveNotes;
    self.addQuote = addQuote;
    self.markWillGetQuote = markWillGetQuote;
    self.markRequestDeclined = markRequestDeclined;
    self.markQuoteToBeExpectedBy = markQuoteToBeExpectedBy;
    self.markOrderPlaced = markOrderPlaced;
    self.markInTransit = markInTransit;
    self.markPartReceived = markPartReceived;
    self.markQuoteSelected = markQuoteSelected;
    self.deleteQuote = deleteQuote;
})
;