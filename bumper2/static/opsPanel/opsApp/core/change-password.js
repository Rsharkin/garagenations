/**
 * Created by inderjeet on 16/5/16.
 */

angular.module('ops.views.changePassword', [
    ])
    .controller('ChangePassCtrl', function ChangePassCtrl($state, $stateParams, $http) {
        var changePassCtrl = this;

        changePassCtrl.ajax_loading = false;
        changePassCtrl.editedForm = {};

        function changePassword() {
            changePassCtrl.ajax_loading = true;
            $http({
                method: 'POST',
                url: '/core/change-password/',
                data:$.param(changePassCtrl.editedForm),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function savePaymentCallBack(){
                changePassCtrl.ajax_loading = false;
                sweetAlert("success", "Password Changed", "success");
                $state.go('base.dashboard');
            },function errorCallback(response, headers, config) {
                changePassCtrl.ajax_loading = false;
                var status = response.status;
                if(status == '401'){
                    sweetAlert("Oops...", "You don't have permission required to do this action.", "error");
                }else if(status == '400'){
                    changePassCtrl.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                }else{
                    sweetAlert("Oops...", "Errors: Unknown", "error");
                }
            });

        }
        changePassCtrl.changePassword = changePassword;
    })
;
