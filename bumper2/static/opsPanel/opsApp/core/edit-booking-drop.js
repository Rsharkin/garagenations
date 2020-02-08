/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingDrop',[
    'ops.services.booking',
    'ops.services.user'
])
    .controller('EditBookingDropCtrl', function EditBookingDropCtrl($state, $scope, $uibModal, BookingService,
                                                                    UserService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();

        function returnToBookings(){
            $state.go('base.bookings',{});
        }

        function cancelEditing(){
            returnToBookings();
        }
        function loadRework(){
            // load rework
            BookingService.getReworkOnBooking(self.booking.id).then(function(response){
                if(response.rework_panels.length>0 || response.rework_packages.length>0){
                    self.hasRework = true;
                }
            });
        }
        function mapData(){
            loadRework();
            for(var i=0;i<self.booking.booking_address.length;i++){
                if(self.booking.booking_address[i].type == 1){
                    self.pickup_address = self.booking.booking_address[i].address;
                }else if(self.booking.booking_address[i].type == 2){
                    self.drop_address = self.booking.booking_address[i].address;
                }
            }
            self.selected_drop_driver = {'id': self.booking.drop_driver};

            BookingService.getBookingBill(self.booking.id).then(function (result) {
                if(result.data) {
                    self.bookingBill = result.data;
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

        function assignDriver(actionToSet) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/assign-driver.html',
                controller: AssignDriverModalInstanceCtrl,
                controllerAs: 'assignDriverCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    driver_for: function () {
                        return 'Drop';
                    },
                    assignmentFor: function () {
                        return 'Driver';
                    },
                    actionToSet: function () {
                        return actionToSet;
                    }
                }
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function updateDropAddress(){
            var modalInstance = $uibModal.open({
                templateUrl: 'views/edit-address.html',
                controller: UserAddressModalInstanceCtrl,
                controllerAs: 'userAddressCtrl',
                resolve: {
                    userId: function () {
                        return self.booking.user;
                    },
                    bookingId: function () {
                        return self.booking.id;
                    },
                    addressType: function () {
                        return 2;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function setDropScheduled(actionToSet){
            if(!self.booking.drop_time || !self.drop_address){
                sweetAlert("Error", "Please enter both drop time and address.", "error");
                return false;
            }
            $scope.editBookingCtrl.setAction(actionToSet);
        }

        function rescheduleDropBooking() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/reschedule-drop.html',
                controller: RescheduleDropModalInstanceCtrl,
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

        function markCarDelivered(actionToSet){
            if(self.bookingBill && self.bookingBill.bill_details.invoice_id && self.bookingBill.bill_details.pay_now !== 3){
                sweetAlert("Error", "Car delivered can be done only when Payment Invoice is settled.", "error");
                return false;
            }
            $scope.editBookingCtrl.setAction(actionToSet);
        }

        function markCarDeliveredCreateRework(){
            swal(
                {
                    title: "Are you sure?",
                    text: "This will create a booking with same user, user car and other details as empty. And Mark this booking car delivered.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Mark Delivered & Create Rework",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.createBooking({
                            'user_id': self.booking.user,
                            'usercar': self.booking.usercar,
                            'city': self.booking.city,
                            'source': 'rework',
                            'rework_booking': self.booking.id
                        }
                    ).then(function(result){
                        $scope.$emit('bookingChanged','');
                        swal(
                            {
                                title: "Rework Booking Created: " + result.data.id,
                                text: "New created booking does not have panel or packages.",
                                type: "success",
                                showCancelButton: true,
                                confirmButtonColor: "#DD6B55",
                                confirmButtonText: "Take me to it!",
                                showLoaderOnConfirm: true,
                                closeOnConfirm: true
                            },
                            function(){
                                $state.go('base.bookings.editBooking', {'bookingId': result.data.id});
                            });

                    });
                });
        }

        function markReadyToGoWithFailedQC(){
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
                        return 'reason_allow_to_go_failed_qc';
                    }
                }
            });
            modalInstance.result.then(function () {
                // Notes taken for reason and already saved.
                $scope.editBookingCtrl.setAction(155); // ACTION_DROP_SCHEDULED_DRIVER_READY_TO_GO_QC_FAILED
            });
        }

        function startReworkOnThisBooking(){
            if(self.hasRework){
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
            }else{
                sweetAlert("Error", "First Add rework to this booking from 'Summary' tab.", "error");

            }
        }

        self.assignDriver = assignDriver;
        self.cancelEditing = cancelEditing;
        self.updateDropAddress=updateDropAddress;
        self.setDropScheduled=setDropScheduled;
        self.rescheduleDropBooking=rescheduleDropBooking;
        self.markCarDelivered=markCarDelivered;
        self.markCarDeliveredCreateRework=markCarDeliveredCreateRework;
        self.markReadyToGoWithFailedQC=markReadyToGoWithFailedQC;
        self.startReworkOnThisBooking=startReworkOnThisBooking;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });
    });