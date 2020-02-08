/**
 * Created by rishisharma on 21/11/16.
 */
angular.module('bumper.view.razorpay', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('RazorPayController', function RazorPayController(UserService,$stateParams,$scope, $rootScope, BUMPER_EVENTS, $location,
                                                                $anchorScroll, $state, $timeout) {
        var self =this;
        self.bookingId=$stateParams.bookingId;
        self.amount=$stateParams.amount;
        $timeout(function goToStatus() {
            $state.go('base.status');
        }, 5000);
    });