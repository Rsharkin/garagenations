/**
 * Created by Indy on 06/02/17.
 */
angular.module('ops.views.editBookingPickup',[
    'ops.services.booking',
    'ops.services.user'
])
    .controller('EditBookingPickupCtrl', function EditBookingPickupCtrl($state, $scope, $uibModal, BookingService,
                                                                        UserService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();

        UserService.getWorkshopManagers().then(function(res){
            self.manager_list = res;
        });

        function updateBookingData(){
            self.booking = BookingService.getCurrentBooking();
            mapData();
        }

        // listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function (event, data) {
            updateBookingData();
        });

        mapData();

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

        function setPickupScheduled(actionToSet){
            if(!self.booking.pickup_time || !self.pickup_address){
                sweetAlert("Error", "Please enter both pickup time and address.", "error");
                return false;
            }
            $scope.editBookingCtrl.setAction(actionToSet);
        }

        function setJobCardUploaded(actionToSet){
            BookingService.getJobCards(self.booking.id)
                .then(function (response) {
                    self.jobCards = response.data.results;
                    var jc_found = false;
                    for(var i=0;i<self.jobCards.length;i++){
                        if(self.jobCards[i].image_type === 1 && self.jobCards[i].image_type){
                            jc_found = true;
                        }
                    }
                    if(jc_found){
                        $scope.editBookingCtrl.setAction(actionToSet);
                    }else{
                        sweetAlert("Error", "First upload job card.", "error");
                        return false;
                    }
                });
        }

        function updatePickUpAddress(){
            var modalInstance = $uibModal.open({
                templateUrl: 'views/edit-address.html',
                controller: UserAddressModalInstanceCtrl,
                controllerAs: 'userAddressCtrl',
                resolve: {
                    userId: function () {
                        return $scope.editBookingCtrl.user.id;
                    },
                    bookingId: function () {
                        return $scope.editBookingCtrl.bookingId;
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

        self.assignDriver = assignDriver;
        self.updatePickUpAddress = updatePickUpAddress;
        self.cancelEditing = cancelEditing;
        self.setPickupScheduled = setPickupScheduled;
        self.setJobCardUploaded = setJobCardUploaded;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });
    });