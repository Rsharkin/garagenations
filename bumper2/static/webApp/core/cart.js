angular.module('bumper.view.cart', [
    'bumper.services.common',
    'bumper.services.user'
])

    .controller('CartController', function CartController($timeout,$location, $anchorScroll, $rootScope, $window, $state, $scope,
                                                          CommonModel, BookingDataService, BUMPER_EVENTS, UserService,CommonService,
                                                          $mdDialog, $mdToast) {
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self = this;
        self.isOpen =false;
        $("img.lazy").lazyload();
        self.openedSignupInScheduleFlow = false;
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
        $scope.$on(BUMPER_EVENTS.CityUpdated, function (event, data) {
            loadBookingDetails();
            loadVasPackages();
        });
        function loadBookingDetails() {
            self.replaceSelected = false;
            var curBooking = BookingDataService.getCurrentBooking();
            self.selectedCarModel = curBooking.selectedCarModel;
            self.selectedPanelList = curBooking.selectedPanelPrices;
            self.selectedPackageList = curBooking.selectedPackages;
            self.dentingCartValue = BookingDataService.dentingCartValue;
            self.cartValue = BookingDataService.cartValue;
            self.totalSaving = BookingDataService.totalSaving;
            self.comments = null;
            if (self.selectedPackageList.length == 0) {
                $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
            }
            var obj = _.find(self.selectedPanelList, function (o) {return o.panel_price.type_of_work_val == 3;});
            if (obj){
                self.replaceSelected = true;
            }

            //console.log(self.selectedPackageList, self.selectedPanelList,self.dentingCartValue,self.cartValue);
        }
        loadBookingDetails();
        function loadVasPackages() {
            var selectedCarModel = BookingDataService.getSelectedCarModel();
            if(selectedCarModel) {
                var city = BookingDataService.getSelectedCityFromLocal();
                CommonModel.loadPackages(selectedCarModel.id, city.id)
                    .then(function (data) {
                        if (data.results) {
                            //console.log('packages ->', data.results);
                            var list_to_show = [];
                            for (var i=0; i< data.results.length; i++){
                                var found = false;
                                for(var j=0;j<self.selectedPackageList.length;j++){
                                    if(self.selectedPackageList[j].id == data.results[i].id){
                                        found = true;
                                        break;
                                    }
                                }
                                if(!found){
                                    list_to_show.push(data.results[i]);
                                }
                            }
                            self.carPackages = list_to_show;
                        }
                    })
            }
        }
        loadVasPackages();

        $scope.$on(BUMPER_EVENTS.BookingChanged, function (event, data) {
            loadBookingDetails();
            loadVasPackages();
        });

        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            if(self.openedSignupInScheduleFlow){
                prepareForScheduling();
            }
        });
        function updateComments(){
            BookingDataService.saveComments(self.comments);
        }

        function prepareForScheduling() {
            // Check user exists otherwise if not go to login screen.
            self.userExist = UserService.getCurrentUser();
            //console.log(" current user-->",self.userExist);
            if (self.userExist)
            {
                var currentBookingFromLocal = BookingDataService.getCurrentBooking();
                //  validation whether we want to go in create booking flow.
                if(!currentBookingFromLocal.selectedCarModel || !currentBookingFromLocal.selectedPackages.length>0 ){
                    $mdDialog.show(
                        $mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .clickOutsideToClose(true)
                            .textContent('No car is selected')
                            .ok('Got it!')
                    );
                    return false;
                }
                //console.log("Create Booking:: current car->",currentBookingFromLocal.selectedCarModel);

                //save user car
                var city = BookingDataService.getSelectedCityFromLocal();
                var selectedYear = null;
                var createBookingData = {
                    "usercar":null,
                    "status":null,
                    "city":city.id,
                    "booking_package":[],
                    "desc":null
                };

                if(currentBookingFromLocal.selectedYear){
                    selectedYear = currentBookingFromLocal.selectedYear.value;
                }
                else{
                    selectedYear = null;
                }
                var res = CommonModel.saveUserCar(currentBookingFromLocal.selectedCarModel.id,selectedYear);
                res.success(function (result) {
                    //console.log("user car saved-->", result);
                    BookingDataService.currentUserCar = result;
                    createBookingData.usercar = result.id;
                    createBookingData.status=1;
                    createBookingData.desc=currentBookingFromLocal.comments;

                    //adding package and panels to booking loadash
                    _(currentBookingFromLocal.selectedPackages).forEach(function (value) {
                        if (value.package.category == 2) {
                            var panelPriceIds = [];
                            _(currentBookingFromLocal.selectedPanelPrices).forEach(function (price) {
                                panelPriceIds.push({'panel': price.panel_price.id})
                            });
                            createBookingData.booking_package.push({"package_id": value.id, "booking_package_panel": panelPriceIds});
                        } else {
                            createBookingData.booking_package.push({"package_id": value.id});
                        }
                    });

                    //console.log("creating booking for ->>>",  createBookingData);

                    var res_booking = CommonModel.createPackageBooking(createBookingData);
                    res_booking.success(function (result) {
                        //console.log('booking created -->', result);
                        //update booking data in services
                        BookingDataService.clearLocalBooking();
                        BookingDataService.bookingDetails=result;
                        // $window.google_trackConversion('http://bumper.com/cart/',{
                        //     google_conversion_id : 946597928,
                        //     google_conversion_label : "5V2RCI6N6mcQqOCvwwM"
                        // });
                        jQuery('body').append('<img height="1" width="1" style="border-style:none;" alt="" src="https://www.googleadservices.com/pagead/conversion/946597928/?label=5V2RCI6N6mcQqOCvwwM&amp;guid=ON&amp;script=0"/>');
                        BookingDataService.clearLocalBookingId();
                        $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged,{});
                        $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 4});
                        $state.go('base.schedule', {'scheduleFor': 'pickup'});
                    }).error(function (result) {
                        $mdDialog.show(
                            $mdDialog.alert()
                                .parent(angular.element(document.querySelector('#popupContainer')))
                                .clickOutsideToClose(true)
                                .textContent('There is some problem with our server. Please try after sometime.')
                                .ok('Got it!')
                        );
                        //console.log('error in booking -->', result);
                    })
                });
            }
            else {
                //console.log("user does not exist");
                self.openedSignupInScheduleFlow = true;
                // setting openingForScheduleFlow = true
                $scope.base.showUserPopup(true, 'Add Pick Up Details button click');
            }
        }
        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            if(self.signupForComments){
                userInquiry(self.comment);
            }
        });

        function userInquiry(action){
            self.comment=action;
            self.userMessage={
                "inquiry":null
            };
            self.userExist=self.userExist = UserService.getCurrentUser();
            if (self.userExist){
                // post enquiry....
                if(self.comment==1){
                    self.userMessage.inquiry="Request for call back";
                }
                else{
                    self.userMessage.inquiry=self.comment;
                }
                var res= CommonModel.sendUserInquiry(self.userMessage);
                res.success(function (result) {
                    self.comments=null;
                    //Show-confirmation
                    self.showSimpleToast = function() {
                        $mdToast.show(
                            $mdToast.simple()
                                .textContent('Thank you! we will call you shortly')
                                .hideDelay(1000)
                                .theme('default')
                        );
                        self.showHelp=false;
                    };
                    self.showSimpleToast();
                }).error( function (result) {
                    self.error=result.inquiry[0];
                })

            }
            else{
                self.signupForComments=true;
                //ask for login ....
                if(self.comment==1){
                    $scope.base.showUserPopup(false, 'Panel Page Request for call back click');
                }else{
                    $scope.base.showUserPopup(false, 'Panel Page comments button click');
                }

            }
        }
        self.userInquiry=userInquiry;
        self.updateComments=updateComments;
        self.prepareForScheduling=prepareForScheduling;
    });