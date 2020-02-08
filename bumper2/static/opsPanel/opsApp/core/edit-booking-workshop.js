/**
 * Created by Indy on 10/02/17.
 */
angular.module('ops.views.editBookingWorkshop',[
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data'
])
    .controller('EditBookingWorkshopCtrl', function EditBookingWorkshopCtrl($state, $scope, BookingService, $uibModal,
                                                                            UserService, CommonService){
        var self = this;
        self.isQCPass = false;
        self.isOldQCPassed = false;
        self.booking = BookingService.getCurrentBooking();
        self.deliveryDesc = self.booking.delivery_reason_desc;
        self.inspectionSheetUploaded = false;
        self.handoverSheetUploaded = false;
        self.eodStatusList = [];

        function loadRework(){
            // load rework
            BookingService.getReworkOnBooking(self.booking.id).then(function(response){
                if(response.rework_panels.length>0 || response.rework_packages.length>0){
                    self.hasRework = true;
                }
            });
        }

        function loadExpectedEOD(){
            BookingService.getExpectedEODList(self.booking.id).then(function(response){
                self.savedExpectedEods = response;
            });
        }

        CommonService.getEntityChanges(self.booking.id).then(function(response){
            self.delays = [];
            var i = 0;
            for(i=0; i < response.length; i++){
                if(response[i].item_tracked === 'estimate_complete_time' || response[i].item_tracked === 'workshop_eta'){
                    self.delays.push(response[i]);
                }
            }
        });

        function getUniqueGroups(array){
            var unique = {},
                distinct = [],
                dataGroupWise = [],
                data = [],
                hasItemsWithIssue = false;

            for( var i in array ){
                if( typeof(unique[array[i].group_num]) == "undefined"){
                    distinct.push(array[i].group_num);
                }
                unique[array[i].group_num] = 0;
            }

            for( var j in distinct ){
                data = _.filter(array,{'group_num':distinct[j]});
                hasItemsWithIssue = _.some(data,
                    function(o){if(o.is_applicable && o.has_issue){return true;} });

                dataGroupWise.push({
                    group_num: distinct[j],
                    created_at: data[0].created_at,
                    updated_by_name: data[0].updated_by_details.name,
                    updated_by_num: data[0].updated_by_details.ops_phone,
                    hasItemsWithIssue:hasItemsWithIssue,
                    data: data
                });
            }
            return dataGroupWise;
        }

        function showChecklistItems(items, typeOfChecklist){
            $uibModal.open({
                templateUrl: typeOfChecklist === 'images'?'views/checklist-images.html': 'views/checklist-details.html',
                controller: ShowChecklistDetailsModalInstanceCtrl,
                controllerAs: 'checklistCtrl',
                resolve: {
                    items: function () {
                        return items;
                    },
                    typeOfChecklist: function () {
                        return typeOfChecklist;
                    }
                }
            });
        }

        BookingService.getQualityChecks(self.booking.id).then(function(res){
            self.testedQualityCheckslGroupWise = getUniqueGroups(res);

            if(res.length>0) {
                self.isQCPass = _.every(res, function (o) {
                    if (!o.is_applicable || (o.is_applicable && !o.has_issue) ) {
                        return true;
                    }
                });
            }
            else{
                self.isQCPass = false;
            }
        });

        BookingService.getOldQualityChecks(self.booking.id).then(function(res){
            self.testedQualityChecksOld = res;
            if(self.testedQualityChecksOld.length>0) {
                self.isOldQCPassed = _.every(self.testedQualityChecksOld, function (o) {
                    if (o.is_passed) {
                        return true;
                    }
                });
            }
            else{
                self.isOldQCPassed = false;
            }
        });
        UserService.getWorkshopManagers().then(function(res){
            self.manager_list = res;
        });

        CommonService.getMasterData(self.booking.city).then(function(res){
            self.workshopList = res.workshops;
            for(var i=0; i< res.ops_statuses.length;i++){
                if(res.ops_statuses[i].flow_order_num >= 311  && res.ops_statuses[i].flow_order_num <= 328){
                    self.eodStatusList.push(res.ops_statuses[i]);
                }
            }

        });

        function returnToBookings(){
            $state.go('base.bookings',{});
        }

        function cancelEditing(){
            returnToBookings();
        }

        function mapData(){
            loadRework();
            loadExpectedEOD();
            self.selected_manager = {'id': self.booking.workshop_manager};
            self.selected_workshop = {'id': self.booking.workshop};

            self.inspectionSheetUploaded = false;
            self.handoverSheetUploaded = false;

            BookingService.getJobCards(self.booking.id)
                .then(function (response) {
                    self.jobCards = response.data.results;
                    var image_found = false;
                    var handover_image_found = false;
                    for(var i=0;i<self.jobCards.length;i++){
                        if(self.jobCards[i].image_type === 4){
                            image_found = true;
                        }
                        if(self.jobCards[i].image_type === 2){
                            handover_image_found = true;
                        }
                    }
                    if(image_found){
                        self.inspectionSheetUploaded = true;
                    }
                    if(handover_image_found){
                        self.handoverSheetUploaded = true;
                    }
                });
        }

        function updateBookingData(){
            self.booking = BookingService.getCurrentBooking();
            mapData();
        }

        // listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function (event, data) {
            updateBookingData();
        });

        mapData();

        function setStatusJobScheduled(actionToSet) {
            if(!self.booking.estimate_complete_time || !self.booking.workshop_eta){
                sweetAlert("error", "Please first update Customer ETA and workshop ETA.", "error");
                return false;
            }
            var hasWork = false;
            var hasPanels = true;
            if(self.booking.booking_package && self.booking.booking_package.length>0){
                hasWork = true;
            }
            var i=0;
            for(i=0; i<self.booking.booking_package.length; i++){
                if(self.booking.booking_package[i].package.package.category===2){
                    if(self.booking.booking_package[i].booking_package_panel.length===0){
                        hasPanels = false;
                    }
                }
            }
            if(!hasWork){
                sweetAlert("error", "No Package/Work added on booking.", "error");
                return false;
            }
            if(!hasPanels){
                sweetAlert("error", "Denting Package is there but no panels.", "error");
                return false;
            }
            BookingService.saveBooking(self.booking.id,{'estimate_complete_time':self.booking.estimate_complete_time},actionToSet).then(function(response){
                self.ajax_loading = false;
                sweetAlert("success", "Booking Updated", "success");
                $scope.$emit('bookingChanged','');
            });
        }

        function setStatusReadyForDelivery(actionToSet){
            if(!self.isQCPass){
                //show Popup for reason
                var modalInstance = $uibModal.open({
                    templateUrl: 'views/reason-qc-failed.html',
                    controller: reasonQcFailController,
                    controllerAs: 'reasonQcFailCtrl',
                    resolve: {
                        bookingId: function () {
                            return self.booking.id;
                        },
                        actionToSet: function () {
                            return actionToSet;
                        },
                        isQCDone: function () {
                            return (self.testedQualityCheckslGroupWise.length > 0);
                        }
                    }
                });
                modalInstance.result.then(function () {
                    $scope.$emit('bookingChanged','');
                });
            }
            else{
                BookingService.saveBooking(self.booking.id,{},actionToSet).then(function(response){
                    self.ajax_loading = false;
                    sweetAlert("success", "Booking Updated", "success");
                    $scope.$emit('bookingChanged','');
                });
            }
        }

        function setStatusPendingPayment(actionToSet) {
            CommonService.getUserCar(self.booking.usercar).then(function (result) {
                self.carRegNo = result.registration_number;
                if(self.carRegNo){
                    BookingService.saveBooking(self.booking.id,{},actionToSet).then(function(response){
                        self.ajax_loading = false;
                        sweetAlert("success", "Booking Updated", "success");
                        $scope.$emit('bookingChanged','');
                    });
                }
                else {
                    sweetAlert("error", "Please first update car registration number ", "error");
                }
            });
        }
        function returnCar() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/return-car.html',
                controller: ReturnCarModalInstanceCtrl,
                controllerAs: 'returnCarCtrl',
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

        function loadWorkshopNotes(){
            BookingService.getWorkshopNotes(self.booking.id).then(function(res){
                self.workshopNotes = res;
            });
        }

        function addWorkshopNotes() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-workshop-notes.html',
                controller: WorkshopNotesModalInstanceCtrl,
                controllerAs: 'workshopNotesCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    bookingCity: function () {
                        return self.booking.city;
                    },
                    purpose: function() {
                        return 'internal_notes';
                    }
                }
            });
            modalInstance.result.then(function () {
                loadWorkshopNotes();
                $scope.$emit('bookingChanged','');
            });
        }
        loadWorkshopNotes();

        function showQCDetails(version){
            var modalInstance = $uibModal.open({
                templateUrl: 'views/quality-check-details.html',
                controller: QualityChecksModalInstanceCtrl,
                controllerAs: 'QCCtrl',
                size: 'lg',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    version: function () {
                        return version;
                    }
                }
            });
        }

        function restartWorkOnBooking(){
            swal(
                {
                    title: "Rework?",
                    text: "This will set booking into 'Work in Progress' status.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Do it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.saveBooking(self.booking.id,{}, 145).then(function(result){
                        $scope.$emit('bookingChanged','');
                        swal("Done!", "Booking Moved back to Work in Progress", "success");
                    });
                });
        }

        function setHandoverSheetUploaded(actionToSet){
            BookingService.getJobCards(self.booking.id)
                .then(function (response) {
                    self.jobCards = response.data.results;
                    var image_found = false;
                    for(var i=0;i<self.jobCards.length;i++){
                        if(self.jobCards[i].image_type === 2){
                            image_found = true;
                        }
                    }
                    if(image_found){
                        BookingService.saveBooking(self.booking.id,{}, actionToSet).then(function(result){
                            BookingService.saveBooking(self.booking.id,{}, 105).then(function(result){
                                $scope.$emit('bookingChanged','');
                                swal("Done!", "Car received in workshop", "success");
                            });
                        });
                    }else{
                        sweetAlert("Error", "First upload handover sheet.", "error");
                        return false;
                    }
                });
        }

        function setInspectionSheetUploaded(actionToSet){
            BookingService.getJobCards(self.booking.id)
                .then(function (response) {
                    self.jobCards = response.data.results;
                    var image_found = false;
                    for(var i=0;i<self.jobCards.length;i++){
                        if(self.jobCards[i].image_type === 4){
                            image_found = true;
                        }
                    }
                    if(image_found){
                        $scope.editBookingCtrl.setAction(actionToSet);
                    }else{
                        sweetAlert("Error", "First upload Inspection sheet.", "error");
                        return false;
                    }
                });
        }

        function setExpectedEOD(){
            self.ajax_loading = true;

            var data = {
                'booking': self.booking.id,
                'for_date': moment().format('YYYY-MM-DD'),
                'status': 13,
                'ops_status': self.expectedEod
            };

            BookingService.setExpectedEOD(data)
                .success(function (response){
                    self.ajax_loading = false;
                    loadExpectedEOD();
                    sweetAlert("success", "Expected EOD Saved", "success");
                })
                .error(function(response, status_code){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(status_code === 400){
                        if(response.detail){
                            self.errorMsg = response.detail;
                        }else{
                            self.errorMsg = 'Please make sure all values are correctly filled.';
                        }
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                })
            ;
        }

        self.setStatusJobScheduled = setStatusJobScheduled;
        self.addWorkshopNotes = addWorkshopNotes;
        self.returnCar = returnCar;
        self.cancelEditing = cancelEditing;
        self.showQCDetails = showQCDetails;
        self.restartWorkOnBooking = restartWorkOnBooking;
        self.setStatusReadyForDelivery = setStatusReadyForDelivery;
        self.setStatusPendingPayment =setStatusPendingPayment;
        self.showChecklistItems = showChecklistItems;
        self.setHandoverSheetUploaded = setHandoverSheetUploaded;
        self.setInspectionSheetUploaded = setInspectionSheetUploaded;
        self.setExpectedEOD = setExpectedEOD;
    });

function reasonQcFailController(bookingId,$uibModalInstance,actionToSet,BookingService, isQCDone){
    var self = this;
    self.ajax_loading = false;
    self.isQCDone = isQCDone;
    self.deliveryReason = "";

    self.ok = function () {
        self.ajax_loading = true;
        self.errorMsgs = [];
        var data = {
            "delivery_reason_desc":self.deliveryReason
        };
        var res = BookingService.saveDeliveryReasonDesc(bookingId,data);
        res.success(function (result) {
            BookingService.saveBooking(bookingId,{},actionToSet).then(function(response) {
                self.ajax_loading = false;
                sweetAlert("success", "Booking Updated", "success");
                $uibModalInstance.close('saved');
            });
        }).error(function (result) {
            //show error
        });
    };
    self.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}