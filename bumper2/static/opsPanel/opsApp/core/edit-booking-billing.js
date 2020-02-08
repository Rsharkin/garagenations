/**
 * Created by Indy on 06/02/17.
 */
angular.module('ops.views.editBookingBilling', [
    'ops.services.booking'
])
    .controller('EditBookingBillingCtrl', function EditBookingBillingCtrl($scope,$timeout, CommonService, BookingService, $uibModal){
        var self = this;
        self.booking = BookingService.getCurrentBooking();
        self.paymentLink = null;
        //get car reg number
        CommonService.getUserCar(self.booking.usercar).then(function(result){
            self.carRegNo = result.registration_number;
        });
        //load and map data on change event
        function mapData(){
            self.booking = BookingService.getCurrentBooking();
            BookingService.getBookingBill(self.booking.id).then(function (result) {
                if(result.data) {
                    self.bookingBill = result.data;
                }
            });

            BookingService.getAppliedCashDiscounts(self.booking.id).then(function (result) {
                if(result.data.results) {
                    self.cashDiscounts = result.data.results;
                }
            });

            BookingService.getPaymentsForBookingData(self.booking.id).then(function (result) {
                if(result.data) {
                    self.payments = result.data;
                }
            });
        }

        // listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function (event, data) {
            mapData();
        });
        mapData();

        //trigger on initiate payment
        function generateInvoice() {
            var res = BookingService.generateInvoice(self.booking.id);
            res.success(function () {
                $scope.$emit('bookingChanged','');
                sweetAlert("Invoice Generated");
            }).error(function () {
                sweetAlert("Error in generating Invoice", "contact admin");
            });
        }

        function generateProformaInvoice() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/generate-proforma-invoice.html',
                controller: ProformaInvoiceModalInstanceCtrl,
                controllerAs: 'proformaInvoiceModalInstanceCtrl',
                resolve: {
                    booking: function() {
                        return self.booking;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        //cancel proforma Invoice
        function cancelProformaInvoice(invoiceId) {
            swal(
                {
                    title: "Are you sure?",
                    text: "This will cancel the Advance payment Invoice and payment link will be invalid.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Cancel it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    var res = BookingService.cancelProformaInvoice(invoiceId);
                    res.success(function () {
                        $scope.$emit('bookingChanged','');
                        sweetAlert("Cancelled Advance Payment Invoice");
                    }).error(function () {
                        sweetAlert("Error in initiating payment", "contact admin");
                    });
                });
        }

        //trigger on initiate payment
        function initiatePayment() {
            var res = BookingService.initiatePayment(self.booking.id, {payment_type: 2});
            res.success(function (result) {
                $scope.$emit('bookingChanged','');
                sweetAlert("Generated Payment Id", result.id);
            }).error(function () {
                sweetAlert("Error in initiating payment", "contact admin");
            });
        }

        //trigger on proforma initiate payment
        function initiateProformaPayment(amount) {
            var res = BookingService.initiateProformaPayment(self.booking.id,
                {payment_type: 2, amount: amount});
            res.success(function (result) {
                $scope.$emit('bookingChanged','');
                sweetAlert("Generated Advance Payment Id", result.id);
            }).error(function () {
                sweetAlert("Error in initiating payment", "contact admin");
            });
        }

        function generatePaymentLink() {
            if(!self.booking.payment_details.pending_payment_id){
                initiatePayment();
            }
            var res = BookingService.generatePaymentLink(self.booking.id);
            res.success(function (result) {
                sweetAlert("Link for direct payment:", "CONFIG_BASE_URL"+"direct-payment/?pid="+result.token);
            }).error(function () {
                sweetAlert("Error in initiating payment link", "contact admin");
            });
        }
        function collectPartialPayment() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/partial-payment.html',
                controller: PartialPaymentModalInstanceCtrl,
                controllerAs: 'partialPaymentModalInstanceCtrl',
                resolve: {
                    booking: function() {
                        return self.booking;
                    }
                }
            });
        }

        self.printDiv = function(divName,bookingId) {
            var printContents = document.getElementById(divName).innerHTML;
            var popupWin = window.open('', '_blank');
            popupWin.document.open();
            popupWin.document.write('' +
                '<html>' +
                '<head>' +
                ' <meta charset="utf-8"> ' +
                ' <meta name="viewport" content="width=device-width, initial-scale=1.0"> ' +
                ' <title>Bumper Invoice for Booking Id'+ bookingId +'</title> ' +
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700,400italic">'+
                ' <link href="/static/libs/css/bootstrap/bootstrap.min.css" rel="stylesheet" type="text/css"> ' +
                ' <link href="/static/libs/css/font-awesome/font-awesome.min.css" rel="stylesheet" type="text/css"> ' +
                ' <link href="/static/libs/css/animate.css/animate.min.css" rel="stylesheet" type="text/css"> ' +
                ' <link href="/static/css/style.css" rel="stylesheet" type="text/css"> ' +
                ' <link href="/static/css/ops-main.css" rel="stylesheet" type="text/css"> ' +
                '</head><body>' +
                '' + printContents + '' +
                '</body></html>' +
                '');
            $timeout(function () {
                popupWin.print();
            },1000);
            popupWin.document.close();
        };

        function showPaymentDetails(txData, errorMessage ) {
            $uibModal.open({
                templateUrl: 'views/payment-details.html',
                controller: ShowPaymentDetailModal,
                controllerAs: "showPaymentDetailModalCtrl",
                resolve: {
                    txData: function() {
                        return txData;
                    },
                    errorMessage: function() {
                        return errorMessage;
                    }
                }
            });
        }

        self.initiatePayment=initiatePayment;
        self.generateInvoice=generateInvoice;
        self.generateProformaInvoice=generateProformaInvoice;
        self.initiateProformaPayment=initiateProformaPayment;
        self.cancelProformaInvoice=cancelProformaInvoice;
        self.generatePaymentLink=generatePaymentLink;
        self.showPaymentDetails=showPaymentDetails;
        self.collectPartialPayment=collectPartialPayment;
    });

function ShowPaymentDetailModal($uibModalInstance, txData, errorMessage){
    var self = this;

    self.txData = txData?txData:'';
    self.errorMessage = errorMessage?errorMessage:'';

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}