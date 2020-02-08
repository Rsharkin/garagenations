/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingDoorstep',[
    'ops.services.booking',
    'ops.services.user'
])
    .controller('EditBookingDoorstepCtrl', function EditBookingDoorstepCtrl($state, $scope, $uibModal, BookingService,
                                                                            UserService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();

        UserService.getWorkshopManagers().then(function(res){
            self.manager_list = res;
        });


        function returnToBookings(){
            $state.go('base.bookings',{});
        }

        function cancelEditing(){
            returnToBookings();
        }

        function mapData(){
            for(var i=0;i<self.booking.booking_address.length;i++){
                if(self.booking.booking_address[i].type == 1){
                    self.pickup_address = self.booking.booking_address[i].address;
                }else if(self.booking.booking_address[i].type == 2){
                    self.drop_address = self.booking.booking_address[i].address;
                }
            }
            self.selected_pickup_driver = {'id': self.booking.pickup_driver};
            self.selected_manager = {'id': self.booking.workshop_manager};

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
                        return 'Pickup';
                    },
                    assignmentFor: function () {
                        return 'Team';
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

        function setPickupScheduled(actionToSet){

            if(!self.booking.pickup_time || !self.pickup_address){
                sweetAlert("Error", "Please enter both pickup time and address.", "error");
                return false;
            }
            $scope.editBookingCtrl.setAction(actionToSet);
        }

        function updatePickUpAddress(){
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
                    addressType: function(){
                        return 1;
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

        self.assignDriver = assignDriver;
        self.updatePickUpAddress = updatePickUpAddress;
        self.cancelEditing = cancelEditing;
        self.setPickupScheduled = setPickupScheduled;
        self.markCarDelivered=markCarDelivered;
        self.markCarDeliveredCreateRework=markCarDeliveredCreateRework;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });
    });