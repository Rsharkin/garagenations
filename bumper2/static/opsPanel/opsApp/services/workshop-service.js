
angular.module('ops.services.workshop',[
])
    .service('WorkshopService', function($http, $q){
        var model = this,
            URLS={
                WORKSHOP_USER_ENDPOINT: '/api/workshop-user/'
            };

        model.getWorkshopUsers = function(){
            return $http.get(URLS.WORKSHOP_USER_ENDPOINT).then(function(response){
                return response.data.results;
            });
        };
    })
;