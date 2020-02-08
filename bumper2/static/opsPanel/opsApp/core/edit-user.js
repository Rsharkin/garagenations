angular.module('ops.views.editUser', [
    'ops.services.user',
    'ops.services.common'
])
    .controller('EditUserCtrl', function EditUserCtrl($state, $scope, $stateParams, UserService, CommonService){
        var self=this;
        self.ajax_loading = false;
        self.user = null;
        self.userCars = null;
        self.userAddresses = null;
        self.userId = $stateParams.userId;

        function loadData(userId) {
            UserService.getUserById(userId)
                .then(function (data) {
                    if(data){
                        self.user = data;
                        self.user.formatedPhone = UserService.getCustomerNumber(self.user.phone);
                    }
                });

            UserService.getUserAddressByUserId(userId)
                .then(function (data) {
                    if(data){
                        self.userAddresses = data.results;
                    }
                });

            CommonService.getUserCarsByUserId(userId)
                .then(function (data) {
                    if(data){
                        self.userCars = data.results;
                    }
                });
            CommonService.getUserCredits(userId)
                .then(function (data) {
                    if(data){
                        self.userCredits = data;
                    }
                });

        }
        loadData(self.userId);
    });
