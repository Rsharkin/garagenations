angular.module('ops.views.raiseAlert', [
    'ops.services.common'
])
    .controller('RaiseAlertCtrl', function RaiseAlertsCtrl(CommonService, $state, $scope){
        var self = this;
        self.newAlert = {};

        CommonService.getMasterData().then(function(res){
            self.teamAlertReasons = res.team_alert_reasons;
            self.workshops = res.workshops;
        });

        function raiseAlert() {
            self.ajax_loading = true;

            self.newAlert.workshop = self.selected_workshop.id != '?' ?self.selected_workshop.id:'';
            self.newAlert.alert_reason = self.selected_team_alert_reason.id != '?' ?self.selected_team_alert_reason.id:'';

            CommonService.raiseAlert(self.newAlert)
                .then(function(response){
                    // console.log(response);
                    self.ajax_loading = false;
                    if(response.status === 201){
                        sweetAlert("success", "Alert saved", "success");
                        $scope.$emit('alertsUpdated','');
                        $state.go('base.alerts', {});
                    }else{
                        sweetAlert("Error", "Errors: Server Error", "error");
                    }
                });
        }

        self.raiseAlert = raiseAlert;
    })
;
