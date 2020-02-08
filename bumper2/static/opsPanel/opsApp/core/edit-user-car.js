angular.module('ops.views.editUserCar', [
    'ops.services.user',
    'ops.services.common'
])
    .controller('EditUserCarCtrl', function EditUserCarCtrl($state, $scope, $stateParams, UserService, CommonService){
        var self=this;
        self.ajax_loading = false;
        self.editedCar = null;
        self.userCarId = $stateParams.userCarId;

        function loadData(userId) {
            CommonService.getUserCar(userId)
                .then(function (data) {
                    if(data){
                        self.editedCar = data;
                        if(self.editedCar.registration_number){
                            var breakup = self.editedCar.registration_number.match(/.{1,2}/g);
                            self.editedCar.registration_number1 = breakup[0];
                            self.editedCar.registration_number2 = breakup[1];
                            self.editedCar.registration_number3 = breakup[2];
                            self.editedCar.registration_number4 = breakup[3] + breakup[4];
                        }
                    }
                });
        }
        loadData(self.userCarId);

        function saveUserCar(){
            self.editedCar.registration_number = self.editedCar.registration_number1 + self.editedCar.registration_number2 + self.editedCar.registration_number3 + self.editedCar.registration_number4;

            CommonService.saveUserCar(self.userCarId, self.editedCar)
                .success(function (response){
                    self.ajax_loading = false;
                    sweetAlert("success", "Car Data Updated", "success");
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

        self.saveUserCar = saveUserCar;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto',
            pickTime: false
        });
    });
