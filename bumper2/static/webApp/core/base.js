angular.module('bumper.view.base', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('BaseCtrl', function self( Lightbox,$log, AuthService, $timeout, $rootScope, $state, $scope, $auth, $window, UserService, $uibModal,
                                           BookingDataService, BUMPER_EVENTS, $location, $anchorScroll, CommonModel, $mdToast, $mdDialog, $analytics,CommonService) {
        var self = this;
        self.selectedCarModel = null;
        self.numOfPackageInCart = 0;
        self.showHelp = false;
        self.successFlag = false;
        self.errorPartnerDetails = null;
        self.showNext = true;
        self.citySelected = false;
        self.isOpen = false;
        self.selectedMode = 'md-scale';
        self.selectedDirection = 'up';
        self.isDeviceMobile = false;
        self.simulateQuery = false;
        self.isDisabled    = false;
        var queryParams = $location.search();
        self.selectedCity = {};
        self.showloc = false;
        self.cityDelhi = {
            "id":2,
            "name":"Gurugram",
            "state":{"name":"Delhi"},
            "is_denting_active":true,
            "is_wash_active":true,
            "default":false
        };
        self.cityBangalore = {
            "id":1,
            "name":"Bengaluru",
            "state":{"name":"Karnataka"},
            "is_denting_active":true,
            "is_wash_active":true,
            "default":false
        };

        Tawk_API = Tawk_API || {};
        self.scrollTop = function () {
            var old = $location.hash();
            $location.hash('headerTop');
            $anchorScroll();
            $location.hash(old);
        };
        $("#tawkchat-minified-wrapper").css('display','block');
        $("img.lazy").lazyload();
        $scope.$on(BUMPER_EVENTS.CityUpdated, function (event, data) {
            loadExistingData();
        });
        $scope.$on(BUMPER_EVENTS.cityDelhi, function (event, data) {
            self.setSelectedCity(self.cityDelhi);
        });
        $scope.$on(BUMPER_EVENTS.cityBangalore, function (event, data) {
            self.setSelectedCity(self.cityBangalore);
        });
        self.selectedCity = BookingDataService.getSelectedCityFromLocal();

        //setting selected city
        self.setSelectedCity = function(city){
            if($state.current.name =='base.schedule' && self.selectedCity.id!=city.id){
                var confirm = $mdDialog.confirm()
                    .title('Change Region?')
                    .textContent('This booking will be cancelled!')
                    .ariaLabel('Are you sure')
                    .ok('Change')
                    .cancel('Cancel');
                $mdDialog.show(confirm).then(function() {
                    self.selectedCity = city;
                    BookingDataService.saveSelectedCityToLocal(city);
                    self.citySelected = true;
                    $rootScope.$broadcast(BUMPER_EVENTS.CityUpdated,{});
                    UserService.changeUserCity(self.selectedCity.id);
                    $state.go("base.estimator");
                });
            }
            else{
                var curBooking = BookingDataService.getCurrentBooking();
                if(self.selectedCity.id==city.id || curBooking.selectedPackages.length==0) {
                    self.selectedCity = city;
                    BookingDataService.saveSelectedCityToLocal(city);
                    self.citySelected = true;
                    $rootScope.$broadcast(BUMPER_EVENTS.CityUpdated,{});
                }
                else{
                    var confirm = $mdDialog.confirm()
                        .title('Change Region?')
                        .textContent('All the items in cart will be removed!')
                        .ariaLabel('Are you sure')
                        .ok('Change')
                        .cancel('Cancel');
                    $mdDialog.show(confirm).then(function() {
                        $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                        self.selectedCity = city;
                        BookingDataService.saveSelectedCityToLocal(city);
                        self.citySelected = true;
                        BookingDataService.clearLocalBooking();
                        $rootScope.$broadcast(BUMPER_EVENTS.CityUpdated,{});
                        $state.go("base.estimator");
                    });
                }
            }
        };

        //setting selected city using params
        self.citySearch = queryParams.utm_source;
        if(self.citySearch){
            self.cityFind = self.citySearch.search("delhi");
            if(self.cityFind!= -1){
                //save delhi to local
                self.setSelectedCity(self.cityDelhi);
            }
            else {
                //save city to local
                self.setSelectedCity(self.cityBangalore);
            }
        }

        /* function to show FAB on popup
         $timeout(function () {
         if (!document.hidden) {
         self.isOpen = true;
         $analytics.eventTrack('FAB opened after 15 sec', {category: 'Home', label: 'Auto FAB open'});
         // do what you need
         }
         }, 15000);
         */
        var storageTestKey = 'test';
        var storage = window.sessionStorage;
        try {
            storage.setItem(storageTestKey, 'test');
            storage.removeItem(storageTestKey);
        } catch (e) {
            if (e.code === DOMException.QUOTA_EXCEEDED_ERR && storage.length === 0) {
                $analytics.eventTrack('Private Mode Detected', {  category: 'Home', label: 'Safari Private Browsing' });
            } else {
            }
        }
        self.isDeviceMobile = CommonService.mobileBrowser();
        if(self.isDeviceMobile ){
            try{
                Tawk_API.showWidget();
            }
            catch (e){
                //tawk api not laded
            }
        }
        if($state.current.name == 'base.payment'
            ||$state.current.name == 'base.paymentWithoutLogin'
            || $state.current.name =='base.feedback'
            || $state.current.name =='base.whatsNext'
            || $state.current.name =='base.inventory'
        ){
            Tawk_API.onLoad = function () {
                Tawk_API.hideWidget();
            };
        }
        if($state.current.name =='base.package'
            || $state.current.name =='base.cart'
            || $state.current.name =='base.status'
            || $state.current.name =='base.feedback'
            || $state.current.name =='base.whatsNext'
            || $state.current.name =='base.inventory'
            || $state.current.name =='base.paymentWithoutLogin'
            && self.isDeviceMobile
        ) {
            Tawk_API.onLoad = function () {
                Tawk_API.hideWidget();
            };
        }else{
            Tawk_API.onLoad = function(){
                Tawk_API.showWidget();
            };
        }
        /* custom Intercom chat launcher
         if ($window.Intercom) {
         $timeout(function () {
         $window.Intercom("boot", {
         app_id: "kvvodsa5",
         custom_launcher_selector: ".custom_chat_button"
         });
         }, 5000)
         }*/
        //youtube frame loading
        self.loadCity = function () {
            CommonModel.getCities().then(function(result){
                self.cities = result.results;
            });
        };

        function loadYoutube(){
            var youtube = document.querySelectorAll( ".youtube" );
            for (var i = 0; i < youtube.length; i++) {
                var source = "https://img.youtube.com/vi/"+ youtube[i].dataset.embed +"/sddefault.jpg";
                var image = new Image();
                image.src = source;
                image.addEventListener( "load", function() {
                    youtube[ i ].appendChild( image );
                }( i ) );
                youtube[i].addEventListener( "click", function() {
                    var iframe = document.createElement( "iframe" );
                    iframe.setAttribute( "frameborder", "0" );
                    iframe.setAttribute( "allowfullscreen", "" );
                    iframe.setAttribute( "src", "https://www.youtube.com/embed/"+ this.dataset.embed +"?rel=0&showinfo=0&autoplay=1" );
                    this.innerHTML = "";
                    this.appendChild( iframe );
                } );
            }
        }
        loadYoutube();

        function chooseCityPopup(){
            var modalInstance = $uibModal.open({
                    templateUrl: 'views/common/city-selection-popup.html',
                    controller: ChooseCityController,
                    controllerAs: 'ccCtrl'
                }
            );
        }

        //search year box query
        /**
         * Search for states... use $timeout to simulate
         * remote dataservice call.
         */
        function querySearch (query) {
            var results = query ? self.states.filter( createFilterFor(query) ) : self.states,
                deferred;
            if (self.simulateQuery) {
                deferred = $q.defer();
                $timeout(function () { deferred.resolve( results ); }, Math.random() * 1000, false);
                return deferred.promise;
            } else {
                return results;
            }
        }

        function searchTextChange(text) {
            //do something when text changes
            $log.info('Text changed to ' + text);
        }

        function selectedYearChange(item) {
            BookingDataService.saveCarYearToLocal(item);
            //do something when year changes
            //$log.info('Item changed to ' + JSON.stringify(item));
        }

        /**
         * Build `states` list of key/value pairs
         */
        function loadAll() {
            var allStates =  '2017, 2016, 2015 , 2014, 2013, 2012, 2011, 2010,\
              2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000, 1999,\
              1998';

            return allStates.split(/, +/g).map( function (state) {
                return {
                    value: state.toLowerCase(),
                    display: state
                };
            });
        }

        /**
         *
         * Create filter function for a query string
         */
        function createFilterFor(query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(state) {
                return (state.value.indexOf(lowercaseQuery) === 0);
            };

        }
        //end
        self.beforeAfterImages = [
            {
                'url':'img/Polo-white-big.png',
                'thumbUrl':'img/Polo-18779.png',
                'name':' Volkswagen Polo',
                'caption':' Volkswagen Polo - Dents Removal & Painting',
                'review':'Great service Got my car cleaned. Loved the service. Kudos to the team.',
                'author':' - Apratim Banerjee'
            },
            {
                'url':'img/City-big.png',
                'thumbUrl':'img/City-18891.png',
                'name':'Honda City',
                'caption':'Honda City -  Dents Removal & Painting',
                'review':'Awesome job hats off I am really impressed with the service and the way the work is done.Its completely flawless...Good job bumper team way to go cheers ;)',
                'author':' - Chitta ranjan Pradhan'
            },
            {
                'url':'img/Rapid-big.png',
                'thumbUrl':'img/Rapid-18394.png',
                'name':'Skoda Rapid',
                'caption':'Skoda Rapid - Dents Removal & Painting'
            },
            {
                'url':'img/Sail-LS-big.png',
                'thumbUrl':'img/Sail-LS-18743.png',
                'name':'Chevrolet Sail',
                'caption':'Chevrolet Sail - Dents Removal  & Painting'
            },
            {
                'url':'img/i20-big.png',
                'thumbUrl':'img/i20-16410.png',
                'name':'Hyundai i20 ',
                'caption':'Hyundai i20 - Dents Removal & Painting',
                'review':'Professional and thorough! Great service with prompt professional communication and timely delivery',
                'author':' - Rajat Srivastava'
            },
            {
                'url':'img/Zest-XT-big.png',
                'thumbUrl':'img/Zest-XT-17962.png',
                'name':'Tata Zest-XT',
                'caption':'Tata Zest-XT - Dents Removal & Painting',
                'review':'They picked my car from home with a professional driver picking it up. Initially it was estimated for evening delivery. But it was not ready they informed me of the delay I was worried to leave a brand new car at an unknown location,but these guys delivered the car at my office the next day with unmatched quality of work.',
                'author':' - Ravi Busi'
            },
            {
                'url':'img/Jaguar-XE-big.png',
                'thumbUrl':'img/Jaguar-XE-18643.png',
                'name':'Jaguar XF',
                'caption':'Jaguar XF - Dents Removal & Painting'
            },
            {
                'url':'img/Beat-big.png',
                'thumbUrl':'img/Beat-18494.png',
                'name':'Chevrolet Beat',
                'caption':'Chevrolet Beat - Dents Removal & Painting',
                'review':'My car is smiling again 5 panel repairs for dents and scratches with paint, job completed in committed time. Finishing is very good as good as new. Very courteous and understanding bumper staff. All work done without any hassles. Best part free pickup and delivery. ',
                'author':' - Divyah'
            },
            {
                'url':'img/Gets-GLX-big.png',
                'thumbUrl':'img/Gets-GLX-18780.png',
                'name':'Hyundai Getz - GLX',
                'caption':'Hyundai Getz - GLX - Dents Removal & Painting'
            }
        ];
        self.beforeAfterImagesMobile = [
            {
                'url':'img/Beat-mobile.png',
                'thumbUrl':'img/Beat-18494.png',
                'name':'Chevrolet Beat',
                'caption':'Chevrolet Beat - Dents Removal & Painting',
                'review':'"My car is smiling again 5 panel repairs for dents and scratches with paint, job completed in committed time. Finishing is very good as good as new. Very courteous and understanding bumper staff. All work done without any hassles. Best part free pickup and delivery." ',
                'author':' - Divyah'
            },
            {
                'url':'img/Polo-white-mobile.png',
                'thumbUrl':'img/Polo-18779.png',
                'name':' Volkswagen Polo',
                'caption':' Volkswagen Polo - Dents Removal & Painting',
                'review':'"Great service Got my car cleaned. Loved the service. Kudos to the team."',
                'author':' - Apratim Banerjee'
            },
            {
                'url':'img/City-mobile.png',
                'thumbUrl':'img/City-18891.png',
                'name':'Honda City',
                'caption':'Honda City -  Dents Removal & Painting',
                'review':'"Awesome job hats off I am really impressed with the service and the way the work is done.Its completely flawless...Good job bumper team way to go cheers ;) "',
                'author':' - Chitta ranjan Pradhan'
            },
            {
                'url':'img/Rapid-mobile.png',
                'thumbUrl':'img/Rapid-18394.png',
                'name':'Skoda Rapid',
                'caption':'Skoda Rapid - Dents Removal & Painting'
            },
            {
                'url':'img/Sail-LS-mobile.png',
                'thumbUrl':'img/Sail-LS-18743.png',
                'name':'Chevrolet Sail',
                'caption':'Chevrolet Sail - Dents Removal  & Painting'
            },
            {
                'url':'img/i20-mobile.png',
                'thumbUrl':'img/i20-16410.png',
                'name':'Hyundai i20 ',
                'caption':'Hyundai i20 - Dents Removal & Painting',
                'review':'"Professional and thorough! Great service with prompt professional communication and timely delivery"',
                'author':' - Rajat Srivastava'
            },
            {
                'url':'img/Zest-XT-mobile.png',
                'thumbUrl':'img/Zest-XT-17962.png',
                'name':'Tata Zest-XT',
                'caption':'Tata Zest-XT - Dents Removal & Painting',
                'review':'"They picked my car from home with a professional driver picking it up. Initially it was estimated for evening delivery. But it was not ready they informed me of the delay I was worried to leave a brand new car at an unknown location,but these guys delivered the car at my office the next day with unmatched quality of work."',
                'author':' - Ravi Busi'
            },
            {
                'url':'img/Jaguar-XE-big.png',
                'thumbUrl':'img/Jaguar-XE-18643.png',
                'name':'Jaguar XF',
                'caption':'Jaguar XF - Dents Removal & Painting'
            },
            {
                'url':'img/Gets-GLX-mobile.png',
                'thumbUrl':'img/Gets-GLX-18780.png',
                'name':'Hyundai Getz - GLX',
                'caption':'Hyundai Getz - GLX - Dents Removal & Painting'
            }
        ];
        self.images = [
            {
                'url': 'img/websiteworkshop-02.jpg',
                'thumbUrl': 'img/thumb2.jpg',
            },
            {
                'url': 'img/websiteworkshop-04.jpg',
                'thumbUrl': 'img/thumb4.jpg'
            },
            {
                'url': 'img/websiteworkshop-07.jpg',
                'thumbUrl': 'img/thumb7.jpg'
            },
            {
                'url': 'img/websiteworkshop-01.jpg',
                'thumbUrl': 'img/thumb8.jpg'
            },
            {
                'url': 'img/websiteworkshop-03.jpg',
                'thumbUrl': 'img/thumb3.jpg'
            },
            {
                'url': 'img/websiteworkshop-08.jpg',
                'thumbUrl': 'img/thumb8.jpg'
            },
            {
                'url': 'img/websiteworkshop-06.jpg',
                'thumbUrl': 'img/thumb6.jpg'
            },
            {
                'url': 'img/websiteworkshop-05.jpg',
                'thumbUrl': 'img/thumb5.jpg'
            }
        ];
        self.openLightboxModal = function (index) {
            Lightbox.openModal(self.images, index);
        };
        self.openBeforeAfterLightboxModal =function(index) {
            Lightbox.openModal(self.beforeAfterImages, index);
        };
        self.openBeforeAfterScreen = function (){
            $state.go('base.beforeAfter');
        };
        $rootScope.$on(BUMPER_EVENTS.BookingUpdated, function () {
            if (self.currentUser) {
                getUserBookingIds();
            }
        });
        $rootScope.$on(BUMPER_EVENTS.BookingChanged, function () {
            if (self.currentUser) {
                getUserBookingIds();
            }
        });
        $rootScope.$on(BUMPER_EVENTS.LoginRequired, function () {
            showUserPopup();
        });
        function getUserBookingIds() {
            CommonModel.getUserBookings().then(function (result) { if (result.data) {
                self.bookingList = result.data.results;
            } });
        }
        $(document).ready(function () {
            $("#owl-demo").owlCarousel({
                navigation : true, // Show next and prev buttons
                slideSpeed : 300,
                paginationSpeed : 400,
                singleItem: true
            });
            //ganesha creative open

        });
        function gotoStatusScreen(bookingId) {
            //saving selected bookingID to local
            BookingDataService.saveSelectedBookingIdtoLocal(bookingId);
            $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);
            $state.go('base.status');
        }
        $scope.$on(BUMPER_EVENTS.StepUpdated, function (event, data) {
            if (data) {
                BookingDataService.saveBookingProgress(data.progress);
                self.progress = data.progress;
            }
        });
        $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": BookingDataService.getBookingProgress()});
        function getParameterByName(name, url) {
            if (!url) url = $window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }
        function getDeviceType(){
            if(navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPad/i) || navigator.userAgent.match(/iPod/i)) {
                // For apple devices
                return 'ios';
            }
            else if(navigator.userAgent.match(/Android/i)
                || navigator.userAgent.match(/webOS/i)
                || navigator.userAgent.match(/BlackBerry/i)
                || navigator.userAgent.match(/Windows Phone/i)){
                // For android or other mobile devices.
                return 'android_and_others';
            }
            else{
                return 'web';
            }
        }
        function setAdCampaignData(){
            var base_url = "https://play.google.com/store/apps/details?id=com.bumper.android&referrer=";
            var utm_source = getParameterByName('utm_source');
            var utm_medium = getParameterByName('utm_medium');
            var utm_campaign = getParameterByName('utm_campaign');

            var deviceType = getDeviceType();
            var default_source = deviceType === 'web'? 'desktop-web': 'mobile-web';
            self.analyticData = {
                utm_source: utm_source?utm_source:default_source,
                utm_medium: utm_medium?utm_medium:'organic',
                utm_campaign: utm_campaign?utm_campaign:'organic'
            };
            BookingDataService.analyticData = self.analyticData;

            if(deviceType === 'ios') {
                // For apple devices
                self.appURL='https://itunes.apple.com/app/apple-store/id1134862260?pt=118116317&ct=test_170717&mt=8';
                self.openAppPopup=false;
            }
            else if(deviceType === 'android_and_others'){
                // For android or other mobile devices.
                self.appURL = base_url + 'utm_source%3D' + self.analyticData.utm_source + '%26utm_medium%3D' + self.analyticData.utm_medium + '%26utm_campaign%3D' + self.analyticData.utm_campaign;
                self.openAppPopup=false;
            }
            else{
                self.openAppPopup=true;
                // if ($window.Intercom) {
                //     $timeout(function () {
                //         $window.Intercom("boot", {
                //             app_id: "kvvodsa5",
                //             custom_launcher_selector: ".custom_chat_button"
                //         });
                //     }, 5000);
                // }
            }

            if(utm_source === 'appredirecturl' && self.appURL){
                $window.location = self.appURL;
                // http://bumper.com/?utm_source=appredirecturl&utm_medium=website&utm_campaign=appinstall
            }
        }
        setAdCampaignData();
        self.currentUser  = UserService.getCurrentUser();
        if(self.currentUser){
            getUserBookingIds();
        }
// listen for the event in the relevant $scope
        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            self.currentUser = UserService.getCurrentUser();
            loadExistingData(data);
            if(self.currentUser){
                getUserBookingIds();
            }
        });
        $scope.$on(BUMPER_EVENTS.BookingChanged, function (event, data) {
            // This is to show number of packages in current cart.
            var curBooking = BookingDataService.getCurrentBooking();
            self.numOfPackageInCart = curBooking.selectedPackages.length;
        });

        function loadExistingData(data){
            // This is used in common functionality in base controller for package and panel add and remove.
            self.selectedCarModel = BookingDataService.getSelectedCarModel();
            self.selectedYear = BookingDataService.getSelectedCarYear();
            var currentLocalBooking = BookingDataService.getCurrentBooking();
            self.numOfPackageInCart = currentLocalBooking.selectedPackages?currentLocalBooking.selectedPackages.length:0;

            // check if booking exists for this user. If it does move to status screen.
            if(self.currentUser && !(data && data.openingForScheduleFlow)){

                // if selected_booking_in in local storage exists. This is when user selects from top menu. using dataservice.
                // then get this latest booking.
                CommonModel.getUserCars().then(function(res){
                    var latestUserCar = res;
                    if(latestUserCar && latestUserCar.length>=1){
                        latestUserCar = latestUserCar[0];
                    }
                    CommonModel.getCurrentBooking(latestUserCar.id, true).then(function (result) {
                        if(result.results.length>0){
                            // TODO Rishi Change this
                            BookingDataService.bookingDetails=result.results[0];
                            /* if($state.current.name !='base.contact'
                             && $state.current.name !='base.schedule'
                             && $state.current.name !='base.payment'
                             && $state.current.name!='base.contactUs'
                             && $state.current.name!='base.about'
                             ){
                             if(BookingDataService.bookingDetails.status.id < 3){
                             $state.go('base.schedule', {'scheduleFor': 'pickup'});
                             }
                             }*/
                        }
                    });
                });
            }
        }
        loadExistingData();

        function logout(){
            UserService.logout();
            $auth.logout();
            BookingDataService.clearLocalStorage();
            $window.location.reload();
            //$window.location='/';
            // TODO Inder review the flow.
        }

        function getApp(){
            var modalInstance = $uibModal.open({
                    templateUrl: 'views/common/get-app.html',
                    controller: getAppController,
                    controllerAs: 'getAppCtrl'
                }
            );
        }
        function openPartnerPopup(){
            var modalInstance = $uibModal.open({
                    templateUrl: 'views/common/partner-popup.html',
                    controller: partnerController,
                    controllerAs:'partnerCtrl'
                }
            );
        }
        function searchCarModel(searchText) {

            if(searchText) {
                return CommonModel.getModel(searchText)
                    .then( function (data) {
                        if (data.results) {
                            return data.results;
                        }
                    } );
            }
            else{
                return CommonModel.getModel()
                    .then( function (data) {
                        if (data.results) {
                            self.popularCars=data.results;
                        }
                    } );
            }
        }
        searchCarModel();

        function keyPressInSearchCar(keyEvent){
            if (keyEvent.which === 13)
                selectedCarModelChanged();

        }

        function selectedCarModelChanged(forScreen){
            var oldSelectedCarModel = BookingDataService.getSelectedCarModel();
            if(!self.selectedCarModel){
                if(forScreen=='panelScreen'){
                    $analytics.eventTrack('Show Panels Button Click', {  category: 'BODE', label: 'No Car Added' });
                }else if(forScreen == 'packageScreen'){
                    $analytics.eventTrack('Show Packages Button Click', {  category: 'All Packages Page', label: 'No Car Added' });
                }
                return false;

            }
            if(oldSelectedCarModel && (oldSelectedCarModel.id != self.selectedCarModel.id)){
                // confirm before changing.
                if(self.numOfPackageInCart > 0 ){
                    var confirm = $mdDialog.confirm()
                        .title('Change Car?')
                        .textContent('All the items in cart will be removed.')
                        .ariaLabel('Are you sure')
                        .ok('Change')
                        .cancel('Cancel');
                    $mdDialog.show(confirm).then(function() {
                        $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                        BookingDataService.saveSelectedCarModel(self.selectedCarModel);
                        BookingDataService.saveCarYearToLocal(self.selectedYear);
                        $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged,{});
                    }, function() {

                        self.selectedCarModel = oldSelectedCarModel;
                        $analytics.eventTrack('Searched Car', {  category: 'BODE', label:self.selectedCarModel.brand.name+"-"+ self.selectedCarModel.name });
                    });
                }else{
                    $analytics.eventTrack('Searched Car', {  category: 'BODE', label:self.selectedCarModel.brand.name+"-"+ self.selectedCarModel.name });
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                    BookingDataService.saveSelectedCarModel(self.selectedCarModel);
                    BookingDataService.saveCarYearToLocal(self.selectedYear);
                    $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged,{});
                }

            }else if(!oldSelectedCarModel){
                $analytics.eventTrack('Searched Car', {  category: 'BODE', label:self.selectedCarModel.brand.name+"-"+ self.selectedCarModel.name });
                $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                BookingDataService.saveSelectedCarModel(self.selectedCarModel);
                BookingDataService.saveCarYearToLocal(self.selectedYear);
                $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged,{});
            }
        }

        function removeSelectedCarModel(){
            if(self.numOfPackageInCart > 0 ) {
                var confirm = $mdDialog.confirm()
                    .title('Change Car?')
                    .textContent('All the items in cart will be removed.')
                    .ariaLabel('Are you sure')
                    .cancel('Cancel')
                    .ok('Change');

                $mdDialog.show(confirm).then(function () {
                    BookingDataService.clearLocalBooking();
                    $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged, {});
                    $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged, {});
                }, function () {

                    //self.selectedCarModel = oldSelectedCarModel;
                });
            }else{
                BookingDataService.clearLocalBooking();
                $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged, {});
                $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged, {});
            }
        }

        function addPackage(pkg){
            BookingDataService.addPackageToBooking(pkg);
            $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 2});
            $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged,{});
        }
        function removePackage(pkg_id){
            BookingDataService.removePackageFromBooking(pkg_id);
            $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged, {});
        };
        function removePanel(panelName){
            BookingDataService.removePanelFromBooking(panelName);
            $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged,{});
        };
        function showUserPopup(openingForScheduleFlow, flowName) {
            var resctrictClose= false;
            var modalInstance = $uibModal.open({
                    templateUrl: 'views/common/signup.html',
                    controller: UserPopupController,
                    controllerAs: 'loginCtrl',
                    resolve: {
                        openingForScheduleFlow: function () {

                            return !openingForScheduleFlow || openingForScheduleFlow == 'false'?null:true;
                        },
                        analyticData: function () {
                            return self.analyticData;
                        },
                        flowName: function () {
                            return flowName;
                        }
                    }
                }
            );
            modalInstance.closed.then(function(){
                if(flowName === 'User request for payment' && !resctrictClose){
                    $state.go('base.home');
                }
            });
            modalInstance.result.then(function(isUserSaved) {
                resctrictClose = true;
                if (flowName === 'User request for payment' && isUserSaved !== 'userSaved') {
                    $state.go('base.home');
                } else if (flowName === 'User Inquiry click' && isUserSaved == 'userSaved') {
                    userInquiry(BookingDataService.userInquiry);
                } else if (flowName === 'Request for call back click' && isUserSaved == 'userSaved'){
                    userInquiry(1);
                }
            });
        }
// $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
//     if(self.signupForComments){
//         userInquiry(self.comment);
//     }
// });
        function userQuery(){
            BookingDataService.userInquiry = '';
            var modalInstance = $uibModal.open({
                controller: QueryController ,
                controllerAs: 'queryCtrl',
                templateUrl: 'views/common/write-query.html',
                clickOutsideToClose:true
            });
            modalInstance.result.then(function(){
                userInquiry(BookingDataService.userInquiry);
            });
        }
        function requestCallback() {
            BookingDataService.userInquiry = '';
            var modalInstance = $uibModal.open({
                controller: CallBackController ,
                controllerAs: 'callBackCtrl',
                templateUrl: 'views/common/request-callback.html',
                clickOutsideToClose:true
            });
            modalInstance.result.then(function(){
                userInquiry(1);
            });
        }
        function userInquiry(comment) {
            self.userExist = UserService.getCurrentUser();
            if(self.userExist){
                var res=CommonService.userInquiry(comment);
                res.success(function (result) {
                    BookingDataService.userInquiry = '';
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
                if(comment == 1){
                    showUserPopup(false, 'Request for call back click');
                }else{
                    showUserPopup(false, 'User Inquiry click');
                }
            }
        };

        self.chooseCityPopup = chooseCityPopup;
        self.loadExistingData=loadExistingData;
        self.gotoStatusScreen=gotoStatusScreen;
        self.openPartnerPopup=openPartnerPopup;
        self.showUserPopup=showUserPopup;
        self.selectedCarModelChanged=selectedCarModelChanged;
        self.keyPressInSearchCar=keyPressInSearchCar;
        self.removeSelectedCarModel=removeSelectedCarModel;
        self.searchCarModel=searchCarModel;
        self.addPackage=addPackage;
        self.removePackage=removePackage;
        self.removePanel=removePanel;
        self.getApp=getApp;
        self.logout = logout;
        self.userInquiry=userInquiry;
        self.userQuery = userQuery;
        self.requestCallback=requestCallback;
        // list of `state` value/display objects
        self.states        = loadAll();
        self.querySearch   = querySearch;
        self.selectedYearChange = selectedYearChange;
        self.searchTextChange   = searchTextChange;
    });
function QueryController($uibModalInstance, BookingDataService) {
    var self=this;
    self.reason =null;
    self.error = null;
    function postQuery(){
        if(self.reason == null){
            self.error = "please enter your query";
        }
        else{
            BookingDataService.userInquiry =self.reason;
            $uibModalInstance.close('');
        }
    }
    self.postQuery = postQuery;
}
function CallBackController($uibModalInstance,$filter) {
    var self=this;
    self.currentDate = new Date();
    self.time = $filter('date')(self.currentDate,'H');
    self.day = $filter('date')(self.currentDate,'EEE');
    if(self.day =='Sun'){
        self.message ='Please request for a call back and our team will definitely reach out to you during working hours - Monday to Saturday, 9 AM to 6 PM';
    }
    else if(self.time>=8 && self.time <18){
        self.message='Our executive will call you within 2 hours'
    }
    else {
        self.message='Please request for a call back and our team will definitely reach out to you during working hours - Monday to Saturday, 9 AM to 6 PM';
    }
    function requestCall(){
        $uibModalInstance.close('');
    }
    self.requestCall = requestCall;
}
function getAppController ($uibModalInstance) {
    var self = this;
    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}
function ChooseCityController($rootScope,BUMPER_EVENTS,$uibModalInstance,BookingDataService) {
    var self = this;
    self.selectedCity = BookingDataService.getSelectedCityFromLocal();
    function setBangalore() {
        $rootScope.$broadcast(BUMPER_EVENTS.cityBangalore,{});
        $uibModalInstance.close('');
    }
    function setDelhi() {
        $rootScope.$broadcast(BUMPER_EVENTS.cityDelhi,{});
        $uibModalInstance.close('');
    }
    self.setBangalore =setBangalore;
    self.setDelhi = setDelhi;
}

function partnerController(CommonModel,$uibModalInstance, $mdToast) {
    var self=this;
    self.partnerDetails = {
        "name": null,
        "workshop_name": null,
        "mobile": null,
        "email": null,
        "utm_source": 'website',
        "utm_medium": 'organic',
        "utm_campaign": 'organic'
    };

    function savePartnerDetails() {
        var res = CommonModel.savePartnerDetails(self.partnerDetails);
        res.success(function (result) {
            self.successFlag = true;
            $uibModalInstance.dismiss('cancel');
            $mdToast.show($mdToast.simple()
                .textContent('Thank you for your Request, We will connect to you shortly!')
                .hideDelay(2000)
                .theme('default'));

        }).error(function (result) {
            self.success = false;
        })
    }
    self.savePartnerDetails=savePartnerDetails;
}


function UserPopupController($window, $rootScope, $scope, $uibModalInstance,UserService, BUMPER_EVENTS, openingForScheduleFlow,

                             BookingDataService,analyticData,$interval, $analytics, flowName) {

    $analytics.pageTrack('/signup');

    var self=this;
    self.signUp=false;
    self.isOtpForSignup = false;
    self.signIn=true;
    self.showOTP=false;
    self.userPhone = null;
    self.signUpDetails = {};
    self.validate_otp_phone = null;
    self.errors = null;
    self.validatePhoneOTP = null;
    self.OtpValidated=false;
    self.timeLeft=180;
    self.timeToShow = '';
    self.timeToShow_message2 = '';
    self.oldSignupDetails = null;
    self.oldLoginDetails = null;
    var intervalPromise;
    self.selectedCity = BookingDataService.getSelectedCityFromLocal();

    function startTimer(){
        self.timeLeft=180;
        self.timeToShow = '';
        self.timeToShow_message2 = '';
        self.oldSignupDetails = null;
        self.oldLoginDetails = null;
        intervalPromise = $interval( function(){
            if(self.timeLeft > 0){
                self.timeLeft -= 1;
                var minutes = parseInt( self.timeLeft / 60 ) % 60;
                var seconds = self.timeLeft % 60;
                self.timeToShow = (minutes < 10 ? "0" + minutes : minutes) + ':' + (seconds  < 10 ? "0" + seconds : seconds);
                if(self.timeLeft == 60){
                    if(self.isOtpForSignup){
                        otpSignup(true, self.oldSignupDetails);
                    }else{
                        requestLoginOtp(true, self.oldLoginDetails);
                    }
                }
            }else{
                var d = new Date();
                var current_hr = d.getHours();
                if(current_hr > 9 && current_hr < 18){
                    self.timeToShow = "Oops! OTP not received.Don't worry we will call you shortly";
                }else{
                    self.timeToShow = "Oops! OTP not received.";
                    self.timeToShow_message2 = "Don't worry we will call you in the morning between 9:00 am to 11:00 am";
                }
            }
        }, 1000, 181);
    }
    function stopTimer(){
        $interval.cancel(intervalPromise);
        self.timeLeft=180;
        self.timeToShow = '';
        self.timeToShow_message2 = '';
        self.oldSignupDetails = null;
        self.oldLoginDetails = null;
    }
    $scope.$on('modal.closing', function(event, reason, closed){
        stopTimer();
    });
    self.close = function () {
        $uibModalInstance.close('');
    };

    if(openingForScheduleFlow){
        self.signUp=true;
        self.isOtpForSignup=true;
        self.signIn=false;
        self.showOTP=false;

    }
    function showLoginScreen(){
        self.signIn=true;
        self.signUp=false;
        self.isOtpForSignup=false;
        self.showOTP=false;
        self.errors = null;
    }
    function showSignUpScreen() {
        self.signUp=true;
        self.isOtpForSignup=true;
        self.signIn=false;
        self.showOTP=false;
        self.errors = null;
    }
    function showOTPScreen() {
        self.signUp=false;
        self.signIn=false;
        self.showOTP=true;
        self.errors = null;
    }
    function requestLoginOtp(doNotResetTimer, retryDetails){
        self.errors = null;
        if(retryDetails){
            self.loginOtpPhone = retryDetails;
        }
        self.oldLoginDetails = self.loginOtpPhone;
        var res = UserService.requestLoginOtp(self.loginOtpPhone);
        res.success(function(result){
            if(!doNotResetTimer){
                startTimer();
            }
            self.userPhone=self.loginOtpPhone;

            showOTPScreen();
        }).error(function(result, status_code){

            if( status_code==400){
                if(result.status){
                    self.errors = result.status;
                }else{
                    self.errors = 'Please fill all fields correctly.';
                }
            }else{
                self.errors = 'Something went wrong on our server. Please try after sometime.';
            }
        });
    }

    function otpSignup(doNotResetTimer, retryDetails){
        if(self.signUpDetails.referral_code==""||self.signUpDetails.referral_code==null){
            delete self.signUpDetails['referral_code'];
        }
        self.errors = null;
        if(retryDetails){
            self.signUpDetails = retryDetails;
        }
        self.oldSignupDetails = self.signUpDetails;

        self.signUpDetails.city_id = self.selectedCity.id; //hardcoded cityid
        self.signUpDetails.device_type = 'web';
        self.signUpDetails.utm_source = analyticData.utm_source;
        self.signUpDetails.utm_medium = analyticData.utm_medium;
        self.signUpDetails.utm_campaign = analyticData.utm_campaign;
        // self.signUpDetails.source = 'web';

        var res = UserService.otpSignup(self.signUpDetails);
        res.success(function(result){
            if(!doNotResetTimer){
                startTimer();
            }
            self.userPhone=self.signUpDetails.phone;

            showOTPScreen();
        }).error(function(result, status_code){

            if( status_code==400){
                if(result.status){
                    self.errors = result.status;
                    if(result.status == 'User already exists. Please login.'){
                        $analytics.eventTrack('Click Sign Up Button', {  category: 'Login/Sign Up Popup', label: 'User Already exist ' + (flowName?flowName:'') });
                    }
                }else{
                    self.errors = 'Please fill all fields correctly.';
                }
            }else{
                self.errors = 'Something went wrong on our server. Please try after sometime.';
            }
        });
    }

    function validateLoginOtp(){
        var res = UserService.login_validate_errors(self.userPhone, self.validatePhoneOTP);
        res.success(function(result){
            self.OtpValidated=true;
            stopTimer();

            UserService.setCurrentUser(result.user);
            $rootScope.$broadcast(BUMPER_EVENTS.UserUpdated,{'openingForScheduleFlow':openingForScheduleFlow});

            if(self.isOtpForSignup){
                $analytics.eventTrack('Click Sign Up Button', {  category: 'Login/Sign Up Popup', label: 'Sign Up Successful ' + (flowName?flowName:'') });
                jQuery('body').append('<img height="1" width="1" style="border-style:none;" alt="" src="https://www.googleadservices.com/pagead/conversion/946597928/?label=uPtrCNOX_mcQqOCvwwM&guid=ON&script=0"/>');
                $window.fbq('track', 'CompleteRegistration');
                jQuery('body').append('<img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=154166655013411&ev=CompleteRegistration&noscript=1"/>');
            }
            $analytics.setUsername(result.user.id);
            $analytics.setUserProperties({ email: result.user.email, userName: result.user.id, name:result.user.name});
            $uibModalInstance.close('userSaved');

        }).error(function(result, status_code){
            if( status_code==400){
                if(result.status){
                    self.errors = result.status;
                    $analytics.eventTrack('Click Sign Up Button', {  category: 'Login/Sign Up Popup', label: 'Sign Up Fail (OTP Validation Failed) ' + (flowName?flowName:'') });
                }else{
                    self.errors = 'Please fill all fields correctly.';
                }
            }else{
                self.errors = 'Something went wrong on our server. Please try after sometime.';
            }
        });
    }

    function checkOTPEntered(){
        if(self.validatePhoneOTP && self.validatePhoneOTP.length >=4){
            validateLoginOtp();
        }
    }

    self.otpSignup=otpSignup;
    self.showSignUpScreen=showSignUpScreen;
    self.showLoginScreen=showLoginScreen;
    self.requestLoginOtp=requestLoginOtp;
    self.validateLoginOtp = validateLoginOtp;
    self.checkOTPEntered = checkOTPEntered;
}