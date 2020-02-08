angular.module('bumper.view.status', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('StatusController', function StatusController($window,$timeout, $location, $anchorScroll,CommonService, BUMPER_EVENTS, $rootScope, $state, CommonModel, BookingDataService, $mdDialog) {

        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self = this;
        self.isOpen = false;
        self.isDeviceMobile = false;
        $("img.lazy").lazyload();
        Tawk_API = Tawk_API || {};
        self.isDeviceMobile = CommonService.mobileBrowser();
        if(self.isDeviceMobile ){
            try{
               Tawk_API.hideWidget();
            }
            catch (e){
                //tawk api not laded
            }
        }
        $rootScope.$on(BUMPER_EVENTS.BookingUpdated, function () {
            updateBookingData();
        });

        function updateBookingData() {
            self.currentBooking = null;
            self.userCarId = null;
            self.bookingId = BookingDataService.getSelectedBookingIdFromLocal();
            if (self.bookingId) {
                //load selected booking by ID
                CommonModel.bookingById(self.bookingId).then(function (result) {
                    if (result.data) {
                        // console.log("booking data", result.data);
                        self.currentBooking = result.data;
                        self.userCarId = result.data.usercar;
                        CommonModel.getUserCarById(self.userCarId).then(function (res) {
                            self.currentCar = res.data;
                        });
                        for (var i = 0; i < self.currentBooking.booking_address.length; i++) {
                            if (self.currentBooking.booking_address[i].type == 1) {
                                self.pickup_address = self.currentBooking.booking_address[i].address;
                            } else if (self.currentBooking.booking_address[i].type == 2) {
                                self.drop_address = self.currentBooking.booking_address[i].address;
                            }
                        }
                        paymentButtonControl();
                    }
                });
            } else {
                CommonModel.getLatestBooking().then(function (res) {
                    if (res) {
                        self.currentBooking = res.latestBooking;
                        self.currentCar = res.latestUserCar;
                        for (var i = 0; i < self.currentBooking.booking_address.length; i++) {
                            if (self.currentBooking.booking_address[i].type == 1) {
                                self.pickup_address = self.currentBooking.booking_address[i].address;
                            } else if (self.currentBooking.booking_address[i].type == 2) {
                                self.drop_address = self.currentBooking.booking_address[i].address;
                            }
                        }
                        paymentButtonControl();
                    }
                });
            }
        }
        updateBookingData();

        function paymentButtonControl() {
            self.paymentStatus = null;
            self.paymentMode = null;
            self.showPaymentButton = false;

            if (self.currentBooking.bill_details.pay_now == 2) {
                self.showPaymentButton = true;
                self.paymentStatus = "Not Paid";
            }
            else{
                if(self.currentBooking.bill_details.pay_now == 3){
                    self.paymentStatus = "Paid";
                }
                self.showPaymentButton = false;
            }
        }

        self.cancelBooking = function() {
            var res= $mdDialog.show({
                controller: DialogCtrl,
                controllerAs: 'ctrl',
                templateUrl: 'views/common/cancellationReasons.html',
                clickOutsideToClose:true,
                resolve: {
                    bookingId: function () {
                        return self.currentBooking.id;
                    }
                }
            })
        };
        function markDeliveryconfirmed(){
            var res=CommonModel.updateBooking(self.currentBooking.id, {'action': 25});
            res.success(function (result) {
                BookingDataService.clearLocalStorage();
                updateBookingData();
                $mdDialog.show(
                    $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .textContent('Thanks for confirming the delivery of car.')
                        .ok('Got it!')
                );
            })
        }
        function payNow(){
            $state.go('base.payment');
        }
        function selectDropLocation(){
            $state.go('base.schedule',{'scheduleFor': 'drop'});
        }
        function addPickupLocation() {
            $state.go('base.schedule',{'scheduleFor': 'pickup'});
        }


        self.markDeliveryconfirmed=markDeliveryconfirmed;
        self.payNow=payNow;
        self.selectDropLocation=selectDropLocation;
        self.paymentButtonControl=paymentButtonControl;
        self.addPickupLocation=addPickupLocation;

    });
function DialogCtrl (BUMPER_EVENTS,$mdDialog,CommonModel,bookingId,BookingDataService,$rootScope) {
    var self = this;
    self.reasonIsEmpty=null;
    self.selectedReason={
        "Id":null,
        "reason":null
    };
    self.textEmpty=null;
    self.otherReason=null;
    self.cancel = function() {
        $mdDialog.cancel();
    };
    /* cancel booking on finish*/
    self.finish = function() {
        var data = {
            'reason_for_cancellation_desc': self.otherReason,
            'cancel_reason_dd': self.selectedReason.Id,
            'action': 24
        };

        function callCancelBooking() {
            var res = CommonModel.updateBooking(bookingId, data);
            res.success(function (result) {
                //BookingDataService.clearLocalStorage();
                $mdDialog.hide();
                BookingDataService.clearLocalBookingId();
                $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);
            })
        };

        //console.log("data for cancellation", data);
        if(data.cancel_reason_dd && data.cancel_reason_dd!=3) {
            callCancelBooking();
        }
        else if(data.cancel_reason_dd==3){
            if(self.otherReason){
                callCancelBooking();
            }else{
                self.textEmpty="please specify the reason";
            }
        }else{
            self.reasonIsEmpty="please select a reason";
            //console.log("reason is empty",self.reasonIsEmpty);
        }
        self.callCancelBooking=callCancelBooking;
    };
    function loadCancellationReasons(){
        CommonModel.loadReasons().then( function (data) {
            self.cancellationReasons=data.data.cancellation_reasons;
            //console.log("reasons data", self.cancellationReasons);

        });
    };
    function setSelectedReason(reason) {
        self.selectedReason.Id=reason.id;
        self.selectedReason.reason=reason.reason;
        //console.log("selected Reason", self.selectedReason);
    };
    function setOtherReason(reason) {
        self.otherReason= reason;
        //console.log("other reason", self.otherReason);
    };
    loadCancellationReasons();
    self.setOtherReason=setOtherReason;
    self.setSelectedReason=setSelectedReason;
    self.loadCancellationReasons=loadCancellationReasons;


};

