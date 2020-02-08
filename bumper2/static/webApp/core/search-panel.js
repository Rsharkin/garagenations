angular.module('bumper.view.carSearch', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('CarPanelSearchController',
        function CarPanelSearchController($timeout,$location, $anchorScroll, $rootScope,
                                          BUMPER_EVENTS,$uibModal, $window, $scope, $state, UserService,
                                          $mdToast, CommonModel, BookingDataService,CommonService, $analytics)
        {
            /*scroll top */
            var old = $location.hash();
            $location.hash('headerTop');
            $anchorScroll();
            $location.hash(old);
            /*-----*/

            /* decalration */
            var self = this;
            self.showHelp = false;
            self.carModels = [];
            self.carPanels = [];
            self.carPackages = [];
            self.readMore = false;
            self.selectedPanelList = [];
            self.cartValue = null;
            self.isCarModelSelected = false;
            self.parts = [];
            self.panels = [];
            self.showPricePopup = false;
            self.replaceSelected = false;
            self.fullBody = {};
            self.isOpen =false;
            self.isFullBodySelected = false;
            self.selectedIndex = 0;
            self.selectedCarModel = BookingDataService.getSelectedCarModel();
            self.selectedCarYear = BookingDataService.getSelectedCarYear();
            var deviceMobile = false;
            $("img.lazy").lazyload();
            try{
                Tawk_API.showWidget();
            }
            catch (e){
                //tawk api not laded
            }

            // listen for the event in the relevant $scope
            $scope.$on('SelectedCarModelChanged', function () {
                updateCarModelAndYear();
                getCarPanels(true);
                removeFullBodyPackage();
                $analytics.eventTrack('Show Panels Button Click', {  category: 'BODE', label: 'Car Added' });
            });
            $scope.$on(BUMPER_EVENTS.CityUpdated, function (event, data) {
                updateCarModelAndYear();
                getCarPanels(true);
                removeFullBodyPackage();
                self.selectedPanelList= [];
            });

            /* car and year update */
            function updateCarModelAndYear() {
                self.selectedCarModel = BookingDataService.getSelectedCarModel();
                self.selectedCarYear = BookingDataService.getSelectedCarYear();
            }

            /* selecting car and tab from Url */
            function loadCarDetailsFromUrl() {
                var queryParams = $location.search();
                if(queryParams.selected_car){
                    if(!self.selectedCarModel || queryParams.selected_car!=self.selectedCarModel.id){
                        CommonModel.getCarInfoByID(queryParams.selected_car).then(function (result) {
                            if(result){
                                BookingDataService.saveSelectedCarModel(result.data);
                                $rootScope.$broadcast(BUMPER_EVENTS.SelectedCarModelChanged,{});
                                $scope.base.loadExistingData();
                            }
                        });
                    }
                }
                if(queryParams.tab){
                    self.selectedIndex = queryParams.tab;
                }
                if(self.selectedIndex==1){
                    loadParts();
                }
                if(self.selectedIndex==2){
                    loadFullBody();
                }
            }
            loadCarDetailsFromUrl();

            /* loading booking details */
            function loadBookingData() {
                var curBooking = BookingDataService.getCurrentBooking();
                self.selectedPanelList = curBooking.selectedPanelPrices;
                var found_obj = _.find(curBooking.selectedPackages, function (o) {
                    if (o.package.category == 3) {
                        return o;
                    }
                });
                if (found_obj) {
                    self.fullBodyInCart = found_obj;
                    selectFullBody(found_obj);
                }
            }
            loadBookingData();

            /*popup for panel price breakup */
            function openBreakupPopup(panel){
                var modalInstance = $uibModal.open({
                    templateUrl: 'views/common/breakup-popup.html',
                    controller: breakupController,
                    controllerAs:'breakupCtrl',
                    resolve: {
                        panel: function(){
                            return panel;
                        }
                    }
                });
            }

            /* load panels */
            function getCarPanels(resetSelectedPanels) {
                //console.log("Car Year",selectedCarYear);
                self.isCarModelSelected = false;
                self.carPanels = [];
                if (resetSelectedPanels) {
                    self.selectedPanelList = [];
                }
                self.carPackages = [];
                self.cartValue = null;

                if (self.selectedCarModel) {
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                    self.isCarModelSelected = true;
                    self.partFlag = false;
                    self.panelFlag = false;
                    if(self.selectedCarYear){
                        //TODO: check the previous model
                        CommonModel.getModelByYear(self.selectedCarModel.id,self.selectedCarYear.value).then(function (data) {
                            if(data){
                                self.selectedCarModel = data.data;
                                loadPanels(self.selectedCarModel);

                            }
                        });
                    }
                    else {
                        loadPanels(self.selectedCarModel);
                    }
                }
            }
            getCarPanels();

            /* load panel */
            function loadPanels(selectedCarModel){
                var city = BookingDataService.getSelectedCityFromLocal();
                var size = "95x72";
                if(deviceMobile){
                    size = "289x219";
                }
                $analytics.pageTrack('/panel-details/');
                CommonModel.getPanel(selectedCarModel.id, city.id, size)
                    .then(function (data) {
                        if (data.results) {
                            self.carPanels = data.results;
                            updateSelectedPanels();
                            if (self.selectedPanelList) {
                                calculateCartValue();
                            }
                        }
                    });

                CommonModel.getDentingPackage(city.id, selectedCarModel.id)
                    .then(function (data) {
                        if (data.results) {
                            self.carPackages = data.results;
                        }
                    });
                if(self.selectedIndex==1){
                    loadParts();
                }
                else if(self.selectedIndex==2){
                    loadFullBody();
                }
            }

            //load parts
            function loadParts() {
                var city = BookingDataService.getSelectedCityFromLocal();
                CommonModel.getPart(self.selectedCarModel.id, city.id)
                    .then(function (data) {
                        if (data.results) {
                            self.parts = data.results;

                            var found_panel = null;
                            for (var i = 0; i < self.parts.length; i++) {
                                found_panel = _.find(self.selectedPanelList, {'panel_name': self.parts[i].name});
                                if (found_panel) {
                                    self.parts[i].selectedTypeOfWork = true;
                                } else {
                                    self.parts[i].selectedTypeOfWork = false;
                                }
                            }
                        }
                    });
            }

            //load full body
            function loadFullBody() {
                var city = BookingDataService.getSelectedCityFromLocal();
                CommonModel.getFullBodyPackage(city.id, self.selectedCarModel.id).then(function (data) {
                    if (data.results) {
                        self.fullBodyPackage = data.results;

                    }
                });
            }

            /* selected panels update  */
            function updateSelectedPanels(){
                var found_panel = null;
                for ( var i=0; i<self.carPanels.length; i++)
                {
                    found_panel = _.find(self.selectedPanelList, { 'panel_name': self.carPanels[i].name });
                    if(found_panel){
                        self.carPanels[i].selectedTypeOfWork = found_panel.panel_price.type_of_work;
                    }else{
                        self.carPanels[i].selectedTypeOfWork = null;
                    }
                }
            }

            // listen for the event in the relevant $scope
            function calculateCartValue(){
                self.savings = 0;
                self.totalForSaving =0;
                self.totalSavingPanel = 0;
                self.fullbodyDealerPrice =0 ;
                var selectedPanel = 0;
                var selectedPart = 0;
                for (var i=0;i<self.selectedPanelList.length;i++){
                    if (self.selectedPanelList[i].panel_price.part_type == 1){
                        selectedPanel +=1;
                    }
                    if (self.selectedPanelList[i].panel_price.part_type == 2){
                        selectedPart +=1;
                    }
                }
                self.selectedPanel = selectedPanel? '('+selectedPanel+')': '';
                self.selectedPart = selectedPart? '('+selectedPart+')': '';
                var obj = _.find(self.selectedPanelList,function (o) {return o.panel_price.type_of_work_val == 3;});
                if(obj){
                    self.replaceSelected = true;
                }
                else {
                    self.replaceSelected = false;
                }
                if(self.isFullBodySelected) {
                    if(self.fullBody.show_savings){
                        self.fullbodyDealerPrice = self.fullBody.dealer_price;
                        self.savings =  self.fullbodyDealerPrice - self.fullBody.price;
                    }
                    if(self.replaceSelected){
                        self.cartValue1 = _.reduce(self.selectedPanelList, function (sum, item) {
                            if (!sum) {
                                sum = 0.0;
                            }
                            if(item.panel_price.show_savings){
                                self.totalForSaving = self.totalForSaving + parseFloat(item.panel_price.new_price);
                                self.totalSavingPanel = self.totalSavingPanel + parseFloat(item.panel_price.dealer_price);
                            }
                            return sum + parseFloat(item.panel_price.new_price);
                        }, null);
                        self.savings = self.savings + (self.totalSavingPanel - self.totalForSaving);
                        self.cartValue = parseFloat(self.fullBody.price) + self.cartValue1;
                    }
                    else{
                        self.cartValue = self.fullBody.price;
                        return  self.fullBody.price;
                    }
                }
                else {
                    self.cartValue = _.reduce(self.selectedPanelList, function (sum, item) {
                        if (!sum) {
                            sum = 0.0;
                        }
                        if(item.panel_price.show_savings){
                            self.totalForSaving = self.totalForSaving + parseFloat(item.panel_price.new_price);
                            self.totalSavingPanel = self.totalSavingPanel + parseFloat(item.panel_price.dealer_price);
                        }
                        return sum + parseFloat(item.panel_price.new_price);
                    }, null);
                    self.savings =  (self.totalSavingPanel) - (self.totalForSaving);
                }
                if(!self.cartValue){
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 1});
                }
            }

            //set selected panels
            function setPanelSelection(panelName, panelPriceItem){
                if(!self.isFullBodySelected || panelPriceItem.type_of_work_val == 3){
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 2});
                    var found_obj = _.find(self.selectedPanelList, { 'panel_name': panelName });
                    if(found_obj){
                        self.selectedPanelList = _.remove(self.selectedPanelList, function(item) {
                            return item.panel_name != panelName;
                        });
                    }
                    self.selectedPanelList.push({'panel_name':panelName, 'panel_price': panelPriceItem});
                    calculateCartValue();
                }
                else{
                    //message to show that panels scratches covered in fullbody panel not added.
                }
            }

            //toggle full body
            function selectFullBody(pkg) {
                $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 2});
                //removing selected panels excluding replace
                var objs = _.remove(self.selectedPanelList, function(o) {
                    if(o.panel_price.type_of_work_val !== 3) return true;
                });

                updateSelectedPanels();
                //console.log('Objs->',objs);
                self.fullBody=pkg;

                self.isFullBodySelected = true;
                calculateCartValue();
            }

            //remove full body
            function removeFullBodyPackage() {
                self.fullBody={};
                self.isFullBodySelected = false;
                calculateCartValue();
            }

            //remove panels
            function removePanelFromSelection(panelName){
                var found_obj = _.find(self.selectedPanelList, { 'panel_name': panelName });
                if(found_obj){
                    self.selectedPanelList = _.remove(self.selectedPanelList, function(item) {
                        return item.panel_name != panelName;
                    });
                }
                calculateCartValue();
            }

            //go to cart
            function moveToCart(){
                if(self.selectedCarModel && self.selectedPanelList.length!=0){
                    // check if full body added remove full body
                    // Add denting as package
                    if(!self.isFullBodySelected && self.fullBodyInCart){
                        BookingDataService.removePackageFromBooking(self.fullBodyInCart.id);
                        $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged, {});
                    }
                    var dentingPackage = _.find(self.carPackages, function(o){ return o.package.category == 2; });
                    BookingDataService.addPackageToBooking(dentingPackage);
                    BookingDataService.replaceAllPanelsOfBooking(self.selectedPanelList);
                    $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged,{});
                    $state.go('base.cart');
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 3});
                }
                if(self.selectedCarModel && self.isFullBodySelected){
                    if(!self.fullBodyInCart){
                        BookingDataService.addPackageToBooking(self.fullBody);
                    }
                    else if(self.fullBodyInCart.id != self.fullBody.id){
                        BookingDataService.removePackageFromBooking(self.fullBodyInCart.id);
                        BookingDataService.addPackageToBooking(self.fullBody);
                    }
                    $rootScope.$broadcast(BUMPER_EVENTS.BookingChanged,{});
                    $state.go('base.cart');
                    $rootScope.$broadcast(BUMPER_EVENTS.StepUpdated, {"progress": 3});
                }
            }
            function showPanelPricePopup() {
                self.showPricePopup = true;
            }
            function hidePanelPricePopup() {
                self.showPricePopup = false;
            }
            self.showPanelPricePopup =showPanelPricePopup;
            self.hidePanelPricePopup = hidePanelPricePopup;
            self.removeFullBodyPackage = removeFullBodyPackage;
            self.selectFullBody = selectFullBody;
            self.setPanelSelection = setPanelSelection;
            self.removePanelFromSelection = removePanelFromSelection;
            self.moveToCart = moveToCart;
            self.openBreakupPopup = openBreakupPopup;
            self.updateCarModelAndYear = updateCarModelAndYear;
            self.loadPanels = loadPanels;
            self.loadParts = loadParts;
            self.loadFullBody = loadFullBody;
        });
function breakupController($uibModalInstance,panel){
    var self= this;
    self.panel = panel;
    self.close = function(){
        $uibModalInstance.close('');
    }
    //console.log("panel",panel);
}

