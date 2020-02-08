angular.module('bumper.view.payment', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('PaymentController', function PaymentController(UserService,$scope, $rootScope, BUMPER_EVENTS, $location,
                                                                $anchorScroll, $state, $timeout, CommonModel,
                                                                BookingDataService,CommonService, $sce, $mdDialog) {
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self = this;
        self.isOpen = false;
        self.modeOfPayment = 1;
        self.citrusFormData = {};
        self.couponCode = null;
        Tawk_API = Tawk_API || {};
        try{
            Tawk_API.hideWidget();
        }
        catch (e){
            //tawk api not laded
        }
        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            paymentProcessor();
        });
        function paymentProcessor() {
            self.userExist = UserService.getCurrentUser();
            if( self.userExist) {
                var queryParams = $location.search();
                if(queryParams.booking_id){
                    self.loadForBooking = queryParams.booking_id;
                }
                $scope.$on(BUMPER_EVENTS.BookingUpdated, function (event) {
                    updateBookingData();
                });

                function updateBookingData() {
                    self.bookingId = BookingDataService.getSelectedBookingIdFromLocal();
                    if (self.bookingId) {
                        //load selected booking by ID
                        CommonModel.bookingById(self.bookingId).then(function (result) {
                            if (result.data) {
                                self.currentBooking = result.data;
                            }
                        });
                        CommonModel.bookingBill(self.bookingId).then(function (res){
                            if(res){
                                self.bill = res.data.bill_details;
                            }
                        });
                    } else {
                        CommonModel.getLatestBooking().then(function (res) {
                            //console.log('fetching latest booking from payment ctrl ->', res);
                            if (res) {
                                self.currentBooking = res.latestBooking;
                                self.currentCar = res.latestUserCar;
                                CommonModel.bookingBill(self.currentBooking.id).then(function (res){
                                    if(res){
                                        self.bill = res.data.bill_details;
                                    }
                                });
                            }
                        });
                    }
                }
                if(!self.loadForBooking) {
                    updateBookingData();
                } else {
                    //TODO function to load booking from server by Id.
                    CommonModel.bookingById( self.loadForBooking).then(function (result) {
                        if (result.data) {
                            // console.log("booking data", result.data);
                            self.currentBooking = result.data;
                        }
                    });
                }
                function applyCoupon() {
                    if (self.couponCode) {
                        var coupon = {"coupon_code": self.couponCode};
                        var res = CommonModel.applyCoupon(self.currentBooking.id, coupon);
                        res.success(function (result, status) {
                            if (status == 206) {
                                self.errors = result.message;
                                $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);
                            } else {
                                //show messages to show successfully coupon applied;
                                self.success = "Coupon applied successfully.Please proceed with the payment here or pay on delivery via cash or card";
                                $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);

                            }

                        }).error(function (result) {
                            self.errors = result.detail;
                            $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);
                        });
                        self.couponCode = null;
                    }
                }
                function deleteCoupon() {
                    var res = CommonModel.deleteCoupon(self.bill.discount_dict.coupon_id);
                    //console.log("coupon deleted", res);
                }
                function checkIfCouponEntered() {
                    if (!self.couponCode) {
                        proceedToPayment();
                    } else{
                        var confirm = $mdDialog.confirm()
                            .title('Coupon Pending!')
                            .textContent('You have a coupon to apply')
                            .ariaLabel('Are you sure')
                            .cancel('Proceed without coupon?')
                            .ok('close')

                        $mdDialog.show(confirm).then(function () {
                            //
                        }, function () {

                            proceedToPayment();
                        });
                    }
                }
                function proceedToPayment() {
                    //deciding the payment gateway
                    CommonModel.bookingBill(self.currentBooking.id).then(function (res) {
                        if(res){
                            self.paymentGateway=res.data.payment_gateway;
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
                            if (self.modeOfPayment == 2) {
                                CommonModel.makePayment(self.currentBooking.id, payment_options)
                                    .then(function (response) {
                                        if (response) {
                                            self.payment_id = response.data.id;
                                            $state.go('base.status');
                                        }
                                    })
                            }else{
                                if(self.paymentGateway===1) {
                                    CommonModel.makePayment(self.currentBooking.id, payment_options)
                                        .then(function (response) {
                                            if (response) {
                                                //console.log('payment save response for PayNow:', response.data);
                                                self.payment_id = response.data.id;
                                                //console.log(" Starting Process for citrus pay for amt-->", self.currentBooking.bill_details.payable_amt);
                                                CommonModel.citrus_pay(self.currentBooking.id, self.payment_id, self.bill.payable_amt)
                                                    .then(function (response) {
                                                        if (response) {
                                                            self.citrusFormData.currency = response.currency;
                                                            self.citrusFormData.formPostUrl = response.formPostUrl;
                                                            self.citrusFormData.merchantTxnId = response.merchantTxnId;
                                                            self.citrusFormData.notify_url = response.notifyUrl;
                                                            self.citrusFormData.orderAmount = response.orderAmount;
                                                            self.citrusFormData.returnUrl = response.returnUrl;
                                                            self.citrusFormData.secSignature = response.secSignature;
                                                            self.citrusFormData.name = response.name;
                                                            self.citrusFormData.email = response.email;
                                                            self.citrusFormData.phoneNumber = response.phoneNumber;
                                                            self.citrusFormData.customParameters = response.customParameters;
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
                                        });
                                }
                                else{
                                    CommonModel.makePayment(self.currentBooking.id, payment_options)
                                        .then(function (response) {
                                            if (response) {
                                                self.payment_id = response.data.id;
                                                self.options = {
                                                    'key': 'CONFIG_RAZORPAY_KEY',
                                                    // Insert the amount here, dynamically, even
                                                    'amount': self.bill.payable_amt*100,
                                                    'name': self.userExist.name,
                                                    'theme': {
                                                        "color": "#795ff9"
                                                    },
                                                    'description': 'Booking Id #'+self.currentBooking.id,
                                                    'handler': function (response) {
                                                        if(response.razorpay_payment_id){
                                                            $state.go('base.razorPay',{bookingId:self.currentBooking.id,amount:self.bill.payable_amt});
                                                        }
                                                    },
                                                    'prefill': {
                                                        'name': self.userExist.name,
                                                        'email': self.userExist.email,
                                                        'contact': self.userExist.phone
                                                    },
                                                    "notes": {
                                                        'bookingId':self.currentBooking.id,
                                                        'paymentId':self.payment_id,
                                                        'used_credits': self.bill.used_credits

                                                    }
                                                }
                                                var rzp1 = new Razorpay(self.options);
                                                rzp1.open();
                                            }
                                        });
                                }
                            }
                        }
                        else{
                            //error in gateway api.
                        }
                    });
                }
                self.trustSrc = function(src) {
                    return $sce.trustAsResourceUrl(src);
                };
                self.deleteCoupon=deleteCoupon;
                self.checkIfCouponEntered = checkIfCouponEntered;
                self.proceedToPayment = proceedToPayment;
                self.applyCoupon = applyCoupon;
            }
            else {
                $scope.base.showUserPopup(false, 'User request for payment');
            }
        }
        paymentProcessor();

    })
;
