angular.module('bumper.view.packages', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('PackagesController', function PackagesController($timeout,$location,$anchorScroll,$window,$scope, $state, CommonModel, BUMPER_EVENTS,
                                                                  BookingDataService,CommonService, $analytics, $rootScope) {
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        var self = this;
        self.carPackages = [];
        self.readMore = false;
        self.isOpen = false;
        self.showLoader = false;
        self.isCarModelSelected = false;
        self.isDeviceMobile = false;
        Tawk_API = Tawk_API || {};
        $("img.lazy").lazyload();
        $("#tawkchat-minified-wrapper").css('display','block');
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
            getPackages();
        });
        var queryParams = $location.search();
        if(queryParams.selected_car){
            CommonModel.getCarInfoByID(queryParams.selected_car).then(function (result) {
                if(result){
                    BookingDataService.saveSelectedCarModel(result.data);
                    $scope.base.loadExistingData();
                    $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged,{});
                }
            });
        }
        function loadBookingDetails() {
            var curBooking = BookingDataService.getCurrentBooking();
            self.selectedPackageList = curBooking.selectedPackages;
            self.cartValue = BookingDataService.cartValue;
            self.isCarModelSelected = false;
            var selectedCarModel = BookingDataService.getSelectedCarModel();
            if (selectedCarModel) {
                self.isCarModelSelected = true;
            }
            //console.log(self.selectedPackageList, self.selectedPanelList,self.cartValue);
        }
        loadBookingDetails();

        function getPackages() {
            var city = BookingDataService.getSelectedCityFromLocal();
            var selectedCarModel = BookingDataService.getSelectedCarModel();
            self.carPackages = [];
            if (selectedCarModel) {
                self.showLoader = true;
                CommonModel.getPackage(city.id, selectedCarModel.id)
                    .then(function (data) {
                        if (data.results) {
                            //console.log( 'Packages ->', data.results );
                            var list_to_show = [],
                                i = 0,
                                j = 0,
                                found = false;
                            for (i = 0; i < data.results.length; i++) {
                                found = false;
                                for (j = 0; j < self.selectedPackageList.length; j++) {
                                    if (self.selectedPackageList[j].id == data.results[i].id) {
                                        found = true;
                                        break;
                                    }
                                }
                                if (!found) {
                                    list_to_show.push(data.results[i]);
                                }
                            }
                            self.carPackages = list_to_show;
                            self.showLoader = false;
                        }
                    });
            }
        }

        getPackages();

        // listen for the event in the relevant $scope
        $scope.$on(BUMPER_EVENTS.SelectedCarModelChanged, function ( event, data) {
            loadBookingDetails();
            getPackages();
            $analytics.eventTrack('Show Packages Button Click', {  category: 'All Packages Page', label: 'Car Added' });
        });
        $scope.$on(BUMPER_EVENTS.BookingChanged, function (event, data) {
            loadBookingDetails();
            getPackages();
        });

        function moveToCart(){
            var selectedCarModel = BookingDataService.getSelectedCarModel();
            var curBooking = BookingDataService.getCurrentBooking();
            if (selectedCarModel && curBooking.selectedPackages) {
                // Move forward only of there are some packages.
                $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 3});
                $state.go('base.cart');
            } else {
                //console.log('Some issue with panels selected, Cannot move to Cart.');
            }
        }
        self.moveToCart = moveToCart;
    });

