angular.module('bumper.view.schedule', [
    'bumper.services.common',
    'bumper.services.user'
])

    .controller('ScheduleController', function ScheduleController($timeout,$rootScope, $location, $anchorScroll, $window, $state, $stateParams, $scope, CommonModel,
                                                                  BookingDataService, $mdDialog,CommonService, BUMPER_EVENTS) {
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self = this;
        self.isOpen = false;
        self.type = 1; // pickup
        self.action = 3; // pickup scheduled
        if($stateParams.scheduleFor == 'drop'){
            self.type = 2; // drop
            self.action = 19; // drop scheduled
        }
        self.is_doorstep = null;
        self.slots = null;
         self.couponCode = null;
        self.addNewAddress = true;
        self.isDateSelected = false;
        self.slotForBooking = null;
        self.currentBooking = null;
        self.addressList = [];
        self.selectedDateIndex = null; // Whatever the default selected index is, use -1 for no selection
        self.selectedTimeIndex = null; // Whatever the default selected index is, use -1 for no selection
        self.userAddressId = null;
        self.comments = null;
        $("img.lazy").lazyload();
        self.userAddress = {
            "alias": null,
            "address": {
                "address1": null,
                "address2": null,
                "pin_code": null,
                "area": null,
                "city": '',
                "state": '',
                "country": null,
                "latitude": 0,
                "longitude": 0
            }
        };
        self.isDeviceMobile = false;
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
        function scrollToAddress() {
            var old = $location.hash();
            $location.hash('.addressScroll');
            $anchorScroll();
            $location.hash(old);
        }

        self.isPickupOnly = false;

        // Getting details of latest booking that was created.
        self.bookingId = BookingDataService.getSelectedBookingIdFromLocal();
        if (self.bookingId) {
            //load selected booking by ID
            CommonModel.bookingById(self.bookingId).then(function (result) {
                if (result.data) {
                    //console.log("booking data", result.data);
                    self.currentBooking = result.data;
                    loadBooking();
                }
            });
        } else {
            CommonModel.getLatestBooking().then(function (res)  {
                // console.log('fetching latest booking from schedule ctrl ->', res);
                if (res) {
                    self.currentBooking = res.latestBooking;
                    self.currentCar = res.latestUserCar;
                    //console.log("Loaded from API current Booking", self.currentBooking);
                    loadBooking();
                }
            });
        }

        function loadBooking() {
            if (self.currentBooking) {
                self.isPickupOnly = _.some(self.currentBooking.booking_package,function (o) {
                    return !o.package.package.is_doorstep;
                });
                if (self.isPickupOnly){
                    self.is_doorstep = false;
                }
                availableSlot();
            }
        }

        function slotsAgainstDate(date) {
            self.date = date;
            self.isDateSelected = true;
            self.choosenSlot =null;
            //console.log("inside slot time calculation",date);
            var timeObj = _.find(self.slots, { 'date': date });
            if (timeObj) {
                self.slotTime =timeObj.slots;
                //console.log("slots for selected date-->",self.slotTime);
            }
        }
        loadBooking();

        function availableSlot() {
            var city = BookingDataService.getSelectedCityFromLocal();
            //console.log("getting available slots -->");
            console.log("curent booking",self.currentBooking);
            CommonModel.get_available_slots(self.currentBooking.usercar,self.type,city.id)
                .then(function (data) {
                    self.slots = data;
                    var dateWithAvailableSlot = _.find(self.slots, function(o) { return o.slots.length > 0; });
                    if (dateWithAvailableSlot) {
                        slotsAgainstDate(dateWithAvailableSlot.date);
                        dateClicked(_.findIndex(self.slots, function(o) { return o.date == dateWithAvailableSlot.date; }));
                    }
                    //console.log("slot data", self.slots);
                });
        }

        function chooseSlot(slotTime) {
            self.choosenSlot = slotTime;
            self.slotForBooking = self.date+" "+slotTime.start_time;
            //console.log('slot time picked',self.slotForBooking);
        }

        function existingUserAddress() {
            CommonModel.userAddresses().then(function (data) {
                if (data) {
                    //console.log("existing addresses -->", self.addressList);
                    self.addressList = data.results;
                    if (self.addressList.length == 0) {
                        self.addNewAddress = true;
                    } else {
                        self.addNewAddress = false;
                    }
                }
            });
        }
        existingUserAddress();

        function getUserAddressId(Id)
        {
            self.userAddressId=Id;
        }

        function saveUserAddress()
        {
            if(self.type == 1 && self.is_doorstep == null){
                $mdDialog.show(
                    $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .textContent('Please select whether you need pickup or service at doorstep.')
                        .ok('Got it!')
                );
                return false;
            }
            //console.log("saving user address",self.userAddress);
            angular.forEach(self.userAddress.address, function (value, key) {
                if (value == "") {
                    self.userAddress.address[key] = null;
                }
            });
            //save address
            if (self.userAddress.address.address1 && self.userAddress.address.area && self.userAddress.address.pin_code){
                var res=CommonModel.saveAddress(self.userAddress);
                res.success(function (result){
                    self.userAddressId=result.id;
                    updateBooking();
                }).error(function (result) {
                    //console.log("error in saving address -->",error);
                })
            }
            else {
                $mdDialog.show(
                    $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .textContent('please fill required address fields')
                        .ok('Got it!')
                );
            }};

        function updateBooking() {
            if(self.type == 1 && self.is_doorstep == null){
                $mdDialog.show(
                    $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .textContent('Please select whether you need pickup or service at doorstep.')
                        .ok('Got it!')
                );
                return false;
            }
            if(self.userAddressId){
                //update slot and address
                if(!self.slotForBooking){
                    $mdDialog.show(
                        $mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .clickOutsideToClose(true)
                            .textContent('please select the date and time.')
                            .ok('Got it!')
                    );

                }else{
                    if(self.type == 1){
                        if (self.is_doorstep && self.is_doorstep !== 'false') {
                            self.action = 26;
                        }
                        self.addressAndSlot={
                            'pickup_time':self.slotForBooking,
                            "booking_address":[{"useraddress_id":self.userAddressId,"type":self.type}],
                            'is_doorstep': self.is_doorstep,
                            "action":self.action};
                    }else{
                        self.addressAndSlot={
                            'drop_time':self.slotForBooking,
                            "booking_address":[{"useraddress_id":self.userAddressId,"type":self.type}],
                            "action":self.action};
                    }

                    //console.log('confirming booking-->',self.addressAndSlot);
                    //console.log('bookingId inside address update-->', self.currentBooking.id);
                    CommonModel.updateBooking(self.currentBooking.id, self.addressAndSlot).success(function (result) {
                        //console.log("bookingAddress updated successfully-->",result);
                        jQuery('body').append('<img height="1" width="1" style="border-style:none;" alt="" src="//www.googleadservices.com/pagead/conversion/946597928/?label=guW6CO_ahHMQqOCvwwM&amp;guid=ON&amp;script=0"/>');
                        $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 5});
                        $state.go('base.status');
                    }).error(function (result) {
                        // console.log('error in saving booking address and slot -->',result);
                    })
                }
            }
            else{
                saveUserAddress();
            }
        }
        function dateClicked(index) {
            self.selectedDateIndex = index;
            self.selectedTimeIndex = null;
        }

        function timeClicked(index) {
            self.selectedTimeIndex = index;
        }
        function addressView(){
        }

        function updateComments(){
            BookingDataService.saveComments(self.comments);
        }
        function onSelectGoogleAddress(googleMapData){
            // console.log('googleMapData->', googleMapData);
            if(googleMapData){

                var required_address = '';
                for( var i=0;i<googleMapData.address_component.length;i++){
                    if(googleMapData.address_component[i].types[0]!='country'
                        &&googleMapData.address_component[i].types[0]!='postal_code'
                        &&googleMapData.address_component[i].types[0]!='administrative_area_level_1'
                        &&googleMapData.address_component[i].types[0]!='locality'
                        &&googleMapData.address_component[i].types[0]!='administrative_area_level_2'
                    ){
                        required_address= required_address+googleMapData.address_component[i].long_name+", ";
                    }
                }
                self.userAddress.address.area = required_address;
                self.userAddress.address.city = googleMapData.cityName;
                self.userAddress.address.country = googleMapData.countryCode;
                self.userAddress.address.state = googleMapData.regionName;
                self.userAddress.address.pin_code = googleMapData.zipCodeId ? googleMapData.zipCodeId:self.userAddress.address.pin_code;
                self.userAddress.address.latitude = googleMapData.latitude;
                self.userAddress.address.longitude = googleMapData.longitude? googleMapData.longitude.toFixed(7):self.userAddress.address.longitude;
            }
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

        self.applyCoupon = applyCoupon;
        self.updateComments=updateComments;
        self.dateClicked=dateClicked;
        self.timeClicked=timeClicked;
        self.addressView=addressView;
        self.slotsAgainstDate=slotsAgainstDate;
        self.chooseSlot=chooseSlot;
        self.existingUserAddress=existingUserAddress;
        self.saveUserAddress=saveUserAddress;
        self.updateBooking=updateBooking;
        self.getUserAddressId=getUserAddressId;
        self.scrollToAddress=scrollToAddress;
        self.onSelectGoogleAddress = onSelectGoogleAddress;

    });
