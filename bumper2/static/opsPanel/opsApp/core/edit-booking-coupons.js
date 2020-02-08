/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingCoupons',[
    'ops.services.booking'
])
    .controller('EditBookingCouponCtrl', function EditBookingCouponCtrl($state, $scope, BookingService, CommonService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();
        self.checkCouponCode = null;
        self.couponDetails = null;
        self.applyCouponDetails = null;
        self.applyCouponCode = null;
        self.discountAmounts = null;
        self.discountReason = null;

        BookingService.getAppliedCashDiscounts(self.booking.id).then(function (result) {
            if(result.data.results) {
                self.discountInfo = result.data.results;
            }
        });

        CommonService.getMasterData(self.booking.city).then(function(result){
            self.discountReasons = result.discount_reasons;
        });

        function updateBookingData(){
            self.booking = BookingService.getCurrentBooking();
            BookingService.getAppliedCashDiscounts(self.booking.id).then(function (result) {
                if(result.data.results) {
                    self.discountInfo = result.data.results;
                }
            });
        }
        // listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function (event, data) {
            updateBookingData();
        });

        function checkCoupon(){
            self.ajax_loading = true;
            BookingService.checkCoupon(self.booking.id, self.checkCouponCode)
                .success(function(response){
                    self.ajax_loading = false;
                    if(response.message){
                        sweetAlert("Error", response.message, "error");
                    }else{
                        self.couponDetails = response;
                    }


                })
                .error(function(response){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(response.non_field_errors){
                        self.errorMsg = response.non_field_errors;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                });
        }

        function applyCoupon(){
            self.ajax_loading = true;
            BookingService.applyCoupon(self.booking.id, self.applyCouponCode)
                .success(function(response){
                    self.ajax_loading = false;

                    if(response.message){
                        sweetAlert("Error", response.message, "error");
                    }else{
                        sweetAlert("success", 'Coupon has been applied!', "success");
                        self.applyCouponDetails = response.bill;
                        $scope.$emit('bookingChanged','');
                    }


                })
                .error(function(response){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(response.non_field_errors){
                        self.errorMsg = response.non_field_errors;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                });
        }

        function applyCashDiscount(){
            self.ajax_loading = true;
            BookingService.applyCashDiscount(self.booking.id, self.discountAmounts, self.discountReason,
                self.discountReasonDD)
                .success(function(response){
                    self.ajax_loading = false;
                    if(response.message){
                        sweetAlert("Error", response.message, "error");
                    }else{
                        sweetAlert("success", 'Discount has been applied!', "success");
                        self.discountAmounts = null;
                        self.discountReason = "";
                        $scope.$emit('bookingChanged','');
                        //self.applyCouponDetails = response.bill;
                    }
                })
                .error(function(response){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(response.non_field_errors){
                        self.errorMsg = response.non_field_errors;
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                });
        }

        self.checkCoupon = checkCoupon;
        self.applyCoupon = applyCoupon;
        self.applyCashDiscount = applyCashDiscount;
    });