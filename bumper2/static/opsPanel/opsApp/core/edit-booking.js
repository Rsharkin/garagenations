/*jshint -W018 */
angular.module('ops.views.editBookings', [
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data',
    'ngFileUpload'
])

    .controller('EditBookingCtrl', function EditBookingCtrl($state, $scope, $stateParams, BookingService, UserService,
                                                            booking, CommonService, $uibModal) {
        var self = this;
        self.ajax_loading = false;
        self.user = null;
        self.bookingId = $stateParams.bookingId;
        self.booking = booking;
        self.userDevices = 'Web';
        self.hasRework = false;
        var i=0;

        function loadRework(){
            // load rework
            BookingService.getReworkOnBooking(self.bookingId).then(function(response){
                if(response.rework_panels.length>0 || response.rework_packages.length>0){
                    self.hasRework = true;
                }
            });
        }
        function updateBookingData() {
            self.booking = BookingService.getCurrentBooking();
            loadRework();
            getAvailableFlags();
        }
        loadRework();

        // listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function () {
            updateBookingData();
        });

        function loadUser(userId) {
            UserService.getUserById(userId)
                .then(function (data) {
                    if (data) {
                        self.user = data;
                        self.user.formatedPhone = UserService.getCustomerNumber(self.user.phone);
                        var is_android = _.some(self.user.active_devices,function(o){if(o.device_type==='android' && o.app_version!=='1.00'){return true;} });
                        var is_ios = _.some(self.user.active_devices,function(o){if(o.device_type==='ios'){return true;} });
                        if(is_android){
                            self.userDevices += ', Android';
                        }
                        if(is_ios){
                            self.userDevices += ', IPhone';
                        }
                    }
                });
        }
        loadUser(self.booking.user);

        CommonService.getUserCar(self.booking.usercar)
            .then(function (data) {
                if (data) {
                    self.userCar = data;
                }
            });

        function getAvailableFlags(){
            self.availableFlags = [];

            for(i=0; i<self.flagTypes.length; i++){
                if(! _.find(self.booking.booking_flag,{flag_type:{id:self.flagTypes[i].id}})){
                    self.availableFlags.push(self.flagTypes[i]);
                }
            }
        }

        CommonService.getMasterData(self.booking.city).then(function(data){
            self.inquiryStatus = data.user_inquiry_statuses;
            self.flagTypes = data.flag_types;
            getAvailableFlags();

            UserService.getUserInquiryByUserId(self.booking.user).then(function(res){
                self.userInquiries = res;
            });
        });

        function returnToBookings() {
            $state.go('base.bookings', {});
        }

        // listen for the event in the relevant $scope
        $scope.$on('bookingChanged', function (event, data) {
            BookingService.getBookingById(self.bookingId)
                .then(function (bookingData) {
                    BookingService.setCurrentBooking(bookingData);
                    $scope.$broadcast('bookingUpdated', '');
                });
        });

        function setAction(actionToSet) {
            self.ajax_loading = true;
            if (actionToSet === 14) {

                var found_0_amt_item = false;
                for (i=0; i<self.booking.booking_package.length; i++){

                    if(parseInt(self.booking.booking_package[i].price) <= 0 || isNaN(self.booking.booking_package[i].price)){
                        found_0_amt_item = true;
                        break;
                    }
                    if(self.booking.booking_package[i].package.package.category == 2){
                        for(var j=0; j<self.booking.booking_package[i].booking_package_panel.length; j++){
                            if(parseInt(self.booking.booking_package[i].booking_package_panel[j].price) <= 0 || isNaN(self.booking.booking_package[i].booking_package_panel[j].price)){
                                found_0_amt_item = true;
                                break;
                            }
                        }
                    }
                }

                if(found_0_amt_item){
                    sweetAlert("Error", 'There are package/panel with amt 0, please update price to proceed.', "error");
                    self.ajax_loading = false;
                    return false;
                }
            }

            if(actionToSet === 22 && !(self.booking.payment_details.payment && self.booking.payment_details.payment.tx_status==1) && !self.booking.bill_details.payable_amt === 0 ){
                // Car delivered can not be marked till payment status is paid
                sweetAlert("Error", 'Payment not paid, Car delivered status can be set only after payment is done.', "error");
                self.ajax_loading = false;
                return false;
            }

            for(i=0; i<self.booking.booking_address.length; i++){
                if(self.booking.booking_address[i].type == 1){
                    self.pickup_address = self.booking.booking_address[i].address;
                }else if(self.booking.booking_address[i].type == 2){
                    self.drop_address = self.booking.booking_address[i].address;
                }
            }

            if(actionToSet === 103 && !(self.pickup_address && self.pickup_address.latitude && self.pickup_address.longitude)){
                // ready for pickup can not be marked if lat,long are not updated.
                sweetAlert("Error", 'Latitude, Longitude not updated for pickup address.', "error");
                self.ajax_loading = false;
                return false;
            }
            
            if(actionToSet === 106 && !(self.drop_address && self.drop_address.latitude && self.drop_address.longitude)){
                // ready for drop can not be marked if lat,long are not updated.
                sweetAlert("Error", 'Latitude, Longitude not updated for drop address.', "error");
                self.ajax_loading = false;
                return false;
            }

            BookingService.saveBooking(self.bookingId,{},actionToSet).then(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Booking Status Updated", "success");
                $scope.$emit('bookingChanged','');
            });
        }

        function uploadBookingImage(bookingImageType) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/common/upload-jobcard.html',
                controller: UploadBookingFileModalInstanceCtrl,
                controllerAs: 'uploadBookingFileCtrl',
                resolve: {
                    bookingId: function () {
                        return self.bookingId;
                    },
                    bookingImageType: function(){
                        return bookingImageType;
                    }
                }
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function assignWorkshop() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/assign-workshop.html',
                controller: AssignWorkshopModalInstanceCtrl,
                controllerAs: 'assignWorkshopCtrl',
                resolve: {
                    bookingId: function () {
                        return self.bookingId;
                    },
                    bookingCity: function () {
                        return self.booking.city;
                    }
                }
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }
        function assignWorkshopManager(whoToAssign) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/assign-workshop-manager.html',
                controller: AssignWorkshopManagersModalInstanceCtrl,
                controllerAs: 'assignWorkshopManagerCtrl',
                resolve: {
                    bookingId: function () {
                        return self.bookingId;
                    },
                    whoToAssign: function () {
                        return whoToAssign;
                    }
                }
            });
            modalInstance.result.then(function () {
                // $state.go('base.bookings.editBooking', {'bookingId': self.bookingId});
                // $window.location.reload(true);
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function rescheduleBooking() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/reschedule-pickup.html',
                controller: RescheduleModalInstanceCtrl,
                controllerAs: 'rescheduleCtrl',
                resolve: {
                    booking: function () {
                        return self.booking;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }
        function setETA() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/edit-eta.html',
                controller: SetETAModalInstanceCtrl,
                controllerAs: 'setETAModalInstanceCtrl',
                resolve: {
                    booking: function() {
                        return self.booking;
                    },
                    is_daily_update: function () {
                        return false;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function updateBooking(dataToUpdate){
            self.ajax_loading = true;

            BookingService.saveBooking(self.bookingId, dataToUpdate)
                .success(function (response){
                    self.ajax_loading = false;
                    sweetAlert("success", "Booking Updated", "success");
                    $scope.$emit('bookingChanged','');
                })
                .error(function(response){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(response.non_field_errors){
                        self.errorMsg = response.non_field_errors[0];
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                })
            ;
        }

        function addBookingFlag (flagId) {
            if(flagId === 1){
                var modalInstance = $uibModal.open({
                    templateUrl: 'views/add-booking-flag.html',
                    controller: AddBookingFlagModalCtrl,
                    controllerAs: 'addBookingFlagModalCtrl',
                    resolve: {
                        bookingId: function () {
                            return self.booking.id;
                        },
                        bookingFlags: function () {
                            return self.flagTypes;
                        }
                    }
                });
                modalInstance.result.then(function () {
                    $scope.$emit('bookingChanged','');
                });
            }else{
                var data = {
                    'booking':self.bookingId,
                    'flag_type':flagId
                };
                BookingService.addBookingFlag(data)
                    .success(function(response){
                        $scope.$emit('bookingChanged','');
                        sweetAlert("success", "Flag Added", "success");
                    })
                    .error(function(response){
                        self.ajax_loading = false;
                        var status = response.status;
                        if(status == '401'){
                            sweetAlert("Error", "You don't have permission required to do this action.", "error");
                        }else if(status == '400'){
                            self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                        }else{
                            sweetAlert("Error", "Errors: Server Error", "error");
                        }
                    });
            }
        }

        function removeBookingFlag (flagId) {
            BookingService.removeBookingFlag(flagId)
                .success(function(response){
                    $scope.$emit('bookingChanged','');
                    sweetAlert("success", "Flag Removed", "success");
                })
                .error(function(response){
                    self.ajax_loading = false;
                    var status = response.status;
                    if(status == '401'){
                        sweetAlert("Error", "You don't have permission required to do this action.", "error");
                    }else if(status == '400'){
                        self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                    }else{
                        sweetAlert("Error", "Errors: Server Error", "error");
                    }
                });
        }

        self.returnToBookings = returnToBookings;
        self.assignWorkshopManager = assignWorkshopManager;
        self.assignWorkshop = assignWorkshop;
        self.rescheduleBooking = rescheduleBooking;
        self.setAction = setAction;
        self.updateBooking = updateBooking;
        self.uploadBookingImage = uploadBookingImage;
        self.setETA = setETA;
        self.addBookingFlag = addBookingFlag;
        self.removeBookingFlag = removeBookingFlag;
    });

function UploadBookingFileModalInstanceCtrl($uibModalInstance, bookingId, Upload, bookingImageType,BookingService) {
    var self = this;

    self.ajax_loading = false;
    self.bookingId = bookingId;
    self.bookingImageType = bookingImageType;
    self.panelsList =[];
    self.selected_panel=null;

    BookingService.getPanelList().then(function (result) {
        if(result){
            self.panelList = result.data.results;
        }
    });

    self.uploadJobCard = function (file) {
        self.ajax_loading = true;
        if(bookingImageType==1 && !self.selected_item){
            self.errorMsg = "Please select type of job card.";
            self.ajax_loading = false;
            return false;
        }
        if(!file){
            self.errorMsg = "Please select a file.";
            self.ajax_loading = false;
            return false;
        }
        var data = {
            'booking': bookingId,
            'media': file,
            'jobcard_type': bookingImageType==1 ? self.selected_item:'',
            'image_type': bookingImageType
        };
        if(bookingImageType==3){
            data.panel = self.selected_panel;
        }
        var res = Upload.upload({
            url: '/api/booking-jobcard/',
            data: data
        });

        res.then(function (response) {

            self.ajax_loading = false;
            sweetAlert("success", "File Uploaded", "success");
            $uibModalInstance.close('saved');
        }, function (response, headers, config) {

            self.ajax_loading = false;
            if (response.status > 0){
                if(response.status == 401){
                    sweetAlert("Oops...", "You don't have permission required to do this action.", "error");
                }else if(response.status == 400){
                    self.errorMsg = 'Please make sure all values are correctly filled';
                }else{
                    sweetAlert("Oops...", "Errors: Server Error", "error");
                }
            }else{
                sweetAlert("Oops...", "Errors: Server Error", "error");
            }

        }, function (evt) {
            // Math.min is to fix IE which reports 200% sometimes
            //file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
        });
    };

    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}