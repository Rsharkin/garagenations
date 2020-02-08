/**
 * Created by Indy on 24/07/17.
 */
function partDocForPanelModalInstanceCtrl ($uibModalInstance, BookingService, CommonService, bookingPackagePanelId,
                                           panelName, booking) {
    var self = this;

    self.ajax_loading = false;
    self.updatePartDoc = null;
    self.quotes = null;
    self.selectedQuote = null;
    self.panelName = panelName;
    self.showCreateDocForm = true;
    self.purchaseDoc = {
        "status": 1
    };
    //console.log('panelName',panelName);
    //console.log('booking', booking);

    CommonService.getUserCar(booking.usercar)
        .then(function (data) {
            if(data){
                self.carDetails = data;
                if(self.carDetails.registration_number){
                    var breakup = self.carDetails.registration_number.match(/.{1,2}/g);
                    self.carDetails.registration_number1 = breakup[0];
                    self.carDetails.registration_number2 = breakup[1];
                    self.carDetails.registration_number3 = breakup[2];
                    self.carDetails.registration_number4 = breakup[3] + breakup[4];
                }
            }
        });

    BookingService.getPurchaseRequisitionTermByPartId(bookingPackagePanelId).then(function (data) {
        console.log('partdoc', data);
        if(data && data.id){
            self.updatePartDoc = data;
            self.showCreateDocForm = false;

            BookingService.getPartQuote(self.updatePartDoc.id).then(function (data) {
                self.quotes = data;
            });
        }
    });

    self.quoteAction = function(action){
        var statusToSet = 6;
        if(action === 'Rejected'){
            statusToSet = 7;
        }
        self.ajax_loading = true;
        BookingService.updatePurchaseRequisitionTerm(self.updatePartDoc.id, {'status':statusToSet})
            .then(function () {
                BookingService.updatePartQuote(self.selectedQuote, {'selected':1})
                    .success(function () {
                        self.ajax_loading = false;
                        sweetAlert("success", "Customer "+action + " Part Price !!", "success");
                        $uibModalInstance.close('saved');
                    });
            });
    };

    function createPartDoc(){
        // Booking package panel details not here
        self.purchaseDoc = {
            "booking_part": bookingPackagePanelId,
            "notes":[{"note": self.purchaseDoc.notes}],
            "status": 1
        };
        BookingService.createPurchaseRequisitionTerm(self.purchaseDoc)
            .success(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Request for Part Created", "success");
                $uibModalInstance.close('saved');
            })
            .error(function(response, status_code){
                self.ajax_loading = false;
                self.errorMsg = 'Something went wrong on server.';

                // console.log(response, status_code);
                if(status_code === 400){
                    if(response.detail){
                        self.errorMsg = response.detail;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                }
                sweetAlert("Error", self.errorMsg, "error");
            });
    }

    function saveUserCar(){
        self.carDetails.registration_number = self.carDetails.registration_number1 + self.carDetails.registration_number2 + self.carDetails.registration_number3 + self.carDetails.registration_number4;
        CommonService.saveUserCar(booking.usercar, self.carDetails)
            .success(function (response){
                createPartDoc();
            })
            .error(function(response, status_code){
                self.ajax_loading = false;
                self.errorMsg = 'Something went wrong on server.';

                if(status_code === 400){
                    if(response.details){
                        self.errorMsg = response.details;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                }
                sweetAlert("Error", self.errorMsg, "error");
            })
        ;
    }

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    self.saveUserCar = saveUserCar;
}