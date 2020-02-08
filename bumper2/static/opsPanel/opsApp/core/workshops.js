angular.module('ops.views.workshops',[
    'ops.services.workshop',
    'ops.services.common',
    'ops.services.user'
])
    .controller('WorkshopsCtrl', function WorkshopsCtrl(WorkshopService, $scope, $uibModal){
        var self = this;
        self.ajax_loading = false;

        function fetchWorkshopUsers(){
            self.ajax_loading = true;
            WorkshopService.getWorkshopUsers().then(function(res){
                self.workshopUsers = res;
            });
        }
        fetchWorkshopUsers();

        $scope.$on('WorkshopUserChanged', function (event, data) {
            fetchWorkshopUsers();
        });

        function editWorkshopUser(workshopUserId, role) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/common/workshop-user.tmpl.html',
                controller: WorkshopUserModalInstanceCtrl,
                controllerAs: 'workshopUserCtrl',
                resolve: {
                    workshopUserId: function () {
                        return workshopUserId;
                    },
                    role: function () {
                        return role;
                    }
                }
            });

            modalInstance.result.then(function () {
                $scope.$emit('WorkshopUserChanged','');
            });
        }
        self.editWorkshopUser = editWorkshopUser;
    })
;

function WorkshopUserModalInstanceCtrl($uibModalInstance, WorkshopService, workshopUserId, CommonService, UserService,
                                       role) {
    var self = this;

    self.ajax_loading = false;
    self.workshopUser = {
        'id': workshopUserId,
        'role': role
    };

    CommonService.getMasterData().then(function(data){
        self.workshopList = data.workshops;
    });
    UserService.getWorkshopManagers().then(function(res){
        self.workshopManagerList = res;
    });
    UserService.getWorkshopExecutives().then(function(res){
        self.workshopExecList = res;
    });
    UserService.getWorkshopAssistantManager().then(function(res){
        self.workshopAssistantManagerList = res;
    });

    function saveWorkshopUser(){
        self.ajax_loading = true;

        WorkshopService.saveBooking(workshopUserId, self.workshopUser).then(function(response){
            self.ajax_loading = false;
            $uibModalInstance.close('saved');
            swal("Done!", "Workshop User mapping saved.", "success");
        });
    }

    self.cancel = function () {
        $uibModalInstance.close('cancel');
    };
    self.saveWorkshopUser = saveWorkshopUser;
}