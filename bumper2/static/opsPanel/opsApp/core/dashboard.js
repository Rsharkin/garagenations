/**
 * Created by inderjeet on 1/4/16.
 */
angular.module('ops.views.dashboard', [
    'ops.services.common'
])
    .controller('DashboardCtrl', function DashboardCtrl($http) {
        var self = this;
        // $http.get('http://localhost:8081/api/user/1/').then(function(result){
        //     //console.log('Booking Data::', result.data.data);
        //     return result;
        // });
    })
;
