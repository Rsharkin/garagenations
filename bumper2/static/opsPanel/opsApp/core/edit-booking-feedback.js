/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingFeedback',[
    'ops.services.booking'
])
    .controller('EditBookingFeedbackCtrl', function EditBookingFeedbackCtrl($state, $scope, BookingService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();
        self.editedFeedback = {
            'booking': self.booking.id
        };

        BookingService.getFeedback(self.booking.id)
            .then(function (feedbackData) {
                if(feedbackData){
                    self.editedFeedback = feedbackData;
                }
            });

        BookingService.getCustomerFeedback(self.booking.id)
            .then(function (customerFeedbackData) {
                self.customerFeedbackData = customerFeedbackData;
            });

        function saveFeedback(){
            self.ajax_loading = true;
            if(self.editedFeedback.id){
                BookingService.updateFeedback(self.editedFeedback.id, self.editedFeedback)
                    .success(function(response){
                        self.ajax_loading = false;
                        if(response.message){
                            sweetAlert("Error", response.message, "error");
                        }else{
                            if(self.booking.status.id == 23){
                                BookingService.saveBooking(self.booking.id, {}, 154).then(function(response){
                                    swal("Saved!", "Feedback Updated Successfully!", "success");
                                    $scope.$emit('bookingChanged','');
                                });
                            }else{
                                swal("Saved!", "Feedback Updated Successfully!", "success");
                            }
                        }
                    })
                    .error(function(response){
                        self.ajax_loading = false;
                        self.errorMsg = 'Something went wrong on server.';

                        if(response.non_field_errors){
                            self.errorMsg = response.non_field_errors;
                        }else{
                            self.errorMsg = 'Please make sure all values are correctly filled.';
                        }
                        sweetAlert("Error", self.errorMsg, "error");
                    });
            }else{
                BookingService.createFeedback(self.editedFeedback)
                    .success(function(response){
                        self.ajax_loading = false;
                        if(response.message){
                            sweetAlert("Error", response.message, "error");
                        }else{
                            self.editedFeedback = response;
                            if(self.booking.status.id == 23) {
                                BookingService.saveBooking(self.booking.id,{},154).then(function(response){
                                    swal("Added!", "Feedback Added Successfully!", "success");
                                    $scope.$emit('bookingChanged','');
                                });
                            }else{
                                swal("Added!", "Feedback Added Successfully!", "success");
                            }
                        }
                    })
                    .error(function(response){
                        self.ajax_loading = false;
                        self.errorMsg = 'Something went wrong on server.';

                        if(response.non_field_errors){
                            self.errorMsg = response.non_field_errors;
                        }else{
                            self.errorMsg = 'Please make sure all values are correctly filled.';
                        }
                        sweetAlert("Error", self.errorMsg, "error");
                    });
            }

        }
        self.saveFeedback = saveFeedback;
    });