angular.module('bumper.services.data', [
])
    .service('CommonService', function (UserService,$mdToast,CommonModel) {
        var self = this;
        function mobileBrowser() {
            if( navigator.userAgent.match(/Android/i)
                || navigator.userAgent.match(/webOS/i)
                || navigator.userAgent.match(/iPhone/i)
                || navigator.userAgent.match(/iPad/i)
                || navigator.userAgent.match(/iPod/i)
                || navigator.userAgent.match(/BlackBerry/i)
                || navigator.userAgent.match(/Windows Phone/i)) {
                return true;
            }
            else {
                return false;
            }
        }
        function userInquiry(comment) {
            self.comment = comment;
            self.userMessage = {
                "inquiry": null
            };
            // post enquiry....
            if (self.comment == 1) {
                self.userMessage.inquiry = "Request for call back";
            }
            else {
                self.userMessage.inquiry = self.comment;
            }
            return CommonModel.sendUserInquiry(self.userMessage);
        }
        self.userInquiry = userInquiry;
        self.mobileBrowser =mobileBrowser;
    })
    .service('BookingDataService', function ($state, $window, $rootScope, BUMPER_EVENTS, CommonModel) {
        var self = this;

        self.userInquiry = '';

        self.analyticData = {
            utm_source: 'website',
            utm_medium: '',
            utm_campaign: ''
        };
        self.city = {
            "id":1,
            "name":"Bengaluru",
            "is_denting_active":true,
            "is_wash_active":true,
            "active":true,
            "default":true
        };
        self.dentingCartValue = 0.00;
        self.cartValue = 0.00;
        self.emptyBooking = {
            "id": null,
            "selectedCarModel": null,
            "userAddress": null,
            "pickupTime": null,
            "selectedPanelPrices": [],
            "selectedPackages": [],
            "comments": null,
        };
        self.currentUserCar = null;

        self.bookingDetails = null;
        self.clearLocalBooking = function () {
            self.dentingCartValue = 0.00;
            self.cartValue = 0.00;
            self.saveBookingProgress(0);
            $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 0});
            saveCurrentBookingToLocal(self.emptyBooking);
        };
        self.clearLocalStorage = function () {
            self.clearLocalBooking();
            self.bookingDetails = null;
            self.currentUserCar = {};
            //TODO Rishi clear selected_booking_id
        };
        self.clearLocalBookingId = function () {
            $window.localStorage['selectedId'] = JSON.stringify(null);
        };
        self.clearFeedbackToken = function () {
            $window.localStorage['FeedbackToken'] = JSON.stringify(null);
        };
        function getCity(){
            CommonModel.getCities().then(function(result){
                if(result){
                    console.log('city in data service',result)
                    return result.results;
                }
            });
        }
        function getUserCarById(usercar) {
            CommonModel.getUserCarById(usercar).then(function (res) {
                self.currentUserCar = res.data;
                $rootScope.$broadcast(BUMPER_EVENTS.BookingUpdated);
            });
        }
        function getCurrentBookingFromLocal() {
            var curBooking = $window.localStorage['currentBooking'];
            if (!curBooking) {
                //console.log('No Current Booking in local so setting it to empty booking obj.');
                curBooking = self.emptyBooking;
                saveCurrentBookingToLocal(curBooking);
            } else {
                curBooking = JSON.parse(curBooking)
            }
            //console.log('current booking in local->', curBooking);
            if (curBooking.selectedPackages && !self.cartValue) {
                // for the first time when saveBooking has not been called, calculate cart value here.
                // 'This should happen only once if items are there in cart. i.e calculating cart value at get.
                // Otherwise this will be done at saving of booking.'
                //  This can happen multiple times if only replacement panel is there in cart.
                //console.log('This should happen only once if items are there in cart. i.e calculating ' +
                //'cart value at get. Otherwise this will be done at saving of booking.');
                _calculateCartValue(curBooking);
            }
            return curBooking;
        }
        function saveSelectedBookingIdtoLocal(bookingId) {
            $window.localStorage['selectedId'] = JSON.stringify(bookingId);
        }
        self.saveSelectedCityToLocal = function(city){
            $window.localStorage['city'] = JSON.stringify(city);
        }
        function saveFeedbackToken(token) {
            $window.localStorage['FeedBackToken'] = JSON.stringify(token)
        }
        function saveCarYearToLocal(item) {
            var curBooking= getCurrentBookingFromLocal();
            curBooking.selectedYear = item;
            saveCurrentBookingToLocal(curBooking);
        }
        function getSelectedBookingIdFromLocal() {
            var id = $window.localStorage['selectedId'];
            if(id){
                id = JSON.parse(id);
                return id;
            }
            else {
                return 0;
            }

        };
        function getSelectedCityFromLocal(){
            var city = $window.localStorage['city'];
            if(city){
                city =JSON.parse(city);
                return city;
            }else{
                return self.city;
            }
        };
        function saveCurrentBookingToLocal(booking) {
            //console.log('Saving booking obj->', booking);
            $window.localStorage['currentBooking'] = JSON.stringify(booking);
            _calculateCartValue(booking);
        };
        self.saveBookingProgress = function (progress) {
            $window.localStorage['progress'] = progress;
        };

        self.getBookingProgress = function () {
            return $window.localStorage['progress']?$window.localStorage['progress']:0;
        };

        self.getCurrentBooking = function () {
            return getCurrentBookingFromLocal();
        };
        self.getSelectedCarModel = function () {
            var curBooking = getCurrentBookingFromLocal();
            return curBooking.selectedCarModel;
        };
        self.getSelectedCarYear = function () {
            var curBooking = getCurrentBookingFromLocal();
            return curBooking.selectedYear;
        };
        self.removeSelectedCarModel = function () {
            self.clearLocalBooking();
        };
        self.saveComments=function (comments) {
            var curBooking= getCurrentBookingFromLocal();
            curBooking.comments = comments;
            saveCurrentBookingToLocal(curBooking);
        };
        self.saveSelectedCarModel = function(carModel){
            if(!carModel){
                return 'Valid car model not supplied.'
            }
            var curBooking = getCurrentBookingFromLocal();
            //console.log('curBooking.selectedCarModel->',curBooking);
            var carChanged = false;
            if(curBooking.selectedCarModel){
                if(carModel.id != curBooking.selectedCarModel.id){
                    // Since car model is changing so existing current booking will be cleared and re-set.
                    self.clearLocalBooking();
                    curBooking = getCurrentBookingFromLocal();
                    carChanged = true;
                    //console.log('Existing booking cleared as new selected car set');
                }else{
                    //console.log('Car Model is same.');
                    return carChanged;
                }
            }
            curBooking.selectedCarModel = carModel;
            saveCurrentBookingToLocal(curBooking);
            //console.log('Selected Car set');
            return carChanged;
        };

        self.addPackageToBooking = function(pkg){
            var curBooking = getCurrentBookingFromLocal();
            var found_obj = _.find(curBooking.selectedPackages, { 'id': pkg.id });
            if(found_obj){
                return 'Package already Added'
            }else{

                curBooking.selectedPackages.push(pkg);
            }
            saveCurrentBookingToLocal(curBooking);
        };

        self.removePackageFromBooking = function(pkg_id){
            var curBooking = getCurrentBookingFromLocal();
            var found_obj = _.find(curBooking.selectedPackages, { 'id': pkg_id });
            if(found_obj){
                curBooking.selectedPackages = _.remove(curBooking.selectedPackages, function(item) {
                    if(item.package.category == 2 && item.id == pkg_id){
                        //console.log('since this is denting package. Remove all selected panels.');
                        // since this is denting package. Remove all selected panels.
                        curBooking.selectedPanelPrices = [];
                    }
                    return item.id != pkg_id;
                });
            }else{
                return 'Package not there is current booking.'
            }
            saveCurrentBookingToLocal(curBooking);
        };

        self.addPanelToBooking = function(panelName, panelPriceItem){
            var curBooking = getCurrentBookingFromLocal();
            var found_obj = _.find(curBooking.selectedPanelPrices, { 'panel_name': panelName });
            if(found_obj){
                curBooking.selectedPanelPrices = _.remove(curBooking.selectedPanelPrices, function(item) {
                    return item.panel_name != panelName;
                });
            }
            curBooking.selectedPanelPrices.push({'panel_name':panelName, 'panel_price': panelPriceItem});
            saveCurrentBookingToLocal(curBooking);
        };

        self.replaceAllPanelsOfBooking = function(panelList){
            var curBooking = getCurrentBookingFromLocal();
            curBooking.selectedPanelPrices = panelList;
            saveCurrentBookingToLocal(curBooking);
        };

        self.removePanelFromBooking = function(panelName){
            var curBooking = getCurrentBookingFromLocal();
            var found_obj = _.find(curBooking.selectedPanelPrices, { 'panel_name': panelName });
            if(found_obj){
                curBooking.selectedPanelPrices = _.remove(curBooking.selectedPanelPrices, function(item) {
                    return item.panel_name != panelName;
                });
            }
            saveCurrentBookingToLocal(curBooking);
            if(curBooking.selectedPanelPrices.length == 0){
                // remove denting package if all panels are removed.
                //console.log('Remove denting Panels in booking->',curBooking.selectedPanelPrices,'  ->dentingpack->',_.find(curBooking.selectedPackages, function(o){ return o.package.category == 2; }));
                var dentingPack = _.find(curBooking.selectedPackages, function(o){ return o.package.category == 2; });
                self.removePackageFromBooking(dentingPack.id);
            }
        };

        function _calculateDentingCartValue(curBooking){
            self.totalForSaving = 0.00;
            self.totalSavingPanel = 0.00;
            self.dentingCartValue = _.reduce(curBooking.selectedPanelPrices, function(sum, item) {
                if(!sum){
                    sum=0.0;
                }
                if(item.panel_price.show_savings){
                    self.totalForSaving = self.totalForSaving + parseFloat(item.panel_price.new_price);
                    self.totalSavingPanel = self.totalSavingPanel + parseFloat(item.panel_price.dealer_price);
                }
                return sum  + parseFloat(item.panel_price.new_price);
                //denting value saving
            }, null);
        }

        function _calculateCartValue(curBooking){
            self.savingForPackage = 0.00;
            self.totalForPackageSaving = 0.00;
            self.cartValue = _.reduce(curBooking.selectedPackages, function(sum, item) {
                if(!sum){
                    sum=0.0;
                }
                if(item.package.category !=2){
                    if(item.show_savings){
                        self.savingForPackage = self.savingForPackage + parseFloat(item.dealer_price);
                        self.totalForPackageSaving = self.totalForPackageSaving + parseFloat(item.price);
                    }
                    return sum  + parseFloat(item.price);
                    //package level saving
                }else{
                    return sum;
                }
            }, null);
            _calculateDentingCartValue(curBooking);
            self.cartValue += self.dentingCartValue;

            self.totalSaving = (self.totalSavingPanel + self.savingForPackage)- (self.totalForSaving + self.totalForPackageSaving);
            // total saving
            //console.log('Current Packages in Cal Cart Value->',curBooking.selectedPackages, ', Cart value->', self.cartValue);
        }

        self.saveSelectedBookingIdtoLocal=saveSelectedBookingIdtoLocal;
        self.getSelectedBookingIdFromLocal=getSelectedBookingIdFromLocal;
        self.getUserCarById=getUserCarById;
        self.saveCarYearToLocal=saveCarYearToLocal;
        self.saveFeedbackToken = saveFeedbackToken;
        self.getCity = getCity;
        self.getSelectedCityFromLocal= getSelectedCityFromLocal;
    })
;
