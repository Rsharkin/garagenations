/**
 * Created by rishisharma on 16/01/17.
 */
angular.module('bumper.view.directPayment', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('directPaymentController', function directPaymentController(UserService,$scope, $rootScope, BUMPER_EVENTS, $location,
                                                                            $anchorScroll, $state, $timeout, CommonModel,
                                                                            BookingDataService, $sce, $mdDialog) {
        var self = this;
        $(".bm-header").hide();
        var queryParams = $location.search();
        self.token = queryParams.pid;
        self.citrusFormData = {};
        self.error = null;
        self.amount = null;
        self.isLinkExpired = false;
        self.modeOfPayment = 1;
        $("img.lazy").lazyload();
        $("tawkchat-minified-wrapper").css('display','none');
        if(self.token){
            if(queryParams.t){
                //check expiry time
                self.expiry = queryParams.t;
                var currentTime = new Date();
                self.currentTimeInt = currentTime.setHours(currentTime.getHours());
                if(self.currentTimeInt < queryParams.t){
                    self.isLinkExpired = false;
                }
                else{
                    self.isLinkExpired = true;
                }
            }else{
                //normal flow
                self.isLinkExpired = false;
            }
            if(!self.isLinkExpired) {
                //console.log("getting payment details from token");
                //get payment details from token
                var res = CommonModel.getPaymentDetails(self.token);
                res.success(function (data) {
                    //console.log("data",data);
                    self.bookingData = data;
                    //setting amount for partial payment
                    if (queryParams.a) {
                        self.amount = queryParams.a;
                    }
                    else {
                        self.amount = self.bookingData.bill_details.pending_amt;
                    }
                    //get required details from payment
                    //intialize payment
                    function proceedToPayment() {
                        //console.log("bookingData", self.bookingData);
                        //deciding the payment gateway
                        if (self.bookingData.payment_gateway) {
                            self.paymentGateway = self.bookingData.payment_gateway;
                            if (!self.modeOfPayment) {
                                $mdDialog.show(
                                    $mdDialog.alert()
                                        .parent(angular.element(document.querySelector('#popupContainer')))
                                        .clickOutsideToClose(true)
                                        .textContent('Please select mode of payment')
                                        .ok('Got it!')
                                );
                                return false;
                            }
                            var payment_options = {
                                'payment_type': 2
                            };
                            // TODO add comments
                            if (self.paymentGateway === 1) {
                                if (self.bookingData.payment_details.pending_payment_id) {
                                    //console.log('payment save response for PayNow:', response.data);
                                    self.payment_id = self.bookingData.payment_details.pending_payment_id;
                                    //console.log(" Starting Process for citrus pay for amt-->", self.bookingData.bill_details.payable_amt);
                                    CommonModel.citrus_pay(self.bookingData.id, self.payment_id, self.amount)
                                        .then(function (data) {
                                            if (data) {
                                                self.citrusFormData.currency = data.currency;
                                                self.citrusFormData.formPostUrl = data.formPostUrl;
                                                self.citrusFormData.merchantTxnId = data.merchantTxnId;
                                                self.citrusFormData.notify_url = data.notifyUrl;
                                                self.citrusFormData.orderAmount = data.orderAmount;
                                                self.citrusFormData.returnUrl = data.returnUrl;
                                                self.citrusFormData.secSignature = data.secSignature;
                                                self.citrusFormData.name = data.name;
                                                self.citrusFormData.email = data.email;
                                                self.citrusFormData.phoneNumber = data.phoneNumber;
                                                self.citrusFormData.customParameters = data.customParameters;
                                                $timeout(function () {
                                                    document.getElementById('submitToCitrusBtn').click();
                                                });
                                                //$('#submitToCitrusBtn').click();
                                            }
                                        })
                                }
                                else {
                                    //console.log("Error Processing Citrus Pay. on bumper server.");
                                }
                            }
                            else {
                                if (self.bookingData.payment_details.pending_payment_id) {
                                    self.payment_id = self.bookingData.payment_details.pending_payment_id;
                                    self.options = {
                                        'key': 'CONFIG_RAZORPAY_KEY',
                                        // Insert the amount here, dynamically, even
                                        'amount': self.amount * 100,
                                        'name': self.bookingData.user.name,
                                        'theme': {
                                            "color": "#795ff9"
                                        },
                                        'description': 'Booking Id #' + self.bookingData.id,
                                        'handler': function (response) {
                                            if (response.razorpay_payment_id) {
                                                $state.go('base.razorPay', {
                                                    bookingId: self.bookingData.id,
                                                    amount: self.amount
                                                });
                                            }
                                        },
                                        'prefill': {
                                            'name': self.bookingData.user.name,
                                            'email': self.bookingData.user.email,
                                            'contact': self.bookingData.user.phone
                                        },
                                        "notes": {
                                            'bookingId': self.bookingData.id,
                                            'paymentId': self.payment_id,
                                            'used_credits':self.bookingData.bill_details.used_credits

                                        }
                                    };
                                    //console.log("options",self.options);
                                    var rzp1 = new Razorpay(self.options);
                                    rzp1.open();
                                }
                            }
                        }
                        else {
                            //error in gateway api.
                        }
                    }

                    self.proceedToPayment = proceedToPayment;
                });
                res.error(function (data) {
                    self.error = data;
                    //console.log("error",self.error);
                });
            }
            else {
                self.error="Link is Expired";
            }
        }
        else{
            self.error = "OOPS! Something went wrong";
            //console.log("error",self.error);
        }
    });