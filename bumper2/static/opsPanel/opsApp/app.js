/**
 * Created by inderjeet on 1/4/16.
 */


/**
 * ops Website
 *
 */
(function () {
// get ag-Grid to create an Angular module and register the ag-Grid directive
    agGrid.initialiseAgGridWithAngular1(angular);
    var app = angular.module('ops', [
            'ui.router',                    // Routing
            'oc.lazyLoad',                  // ocLazyLoad
            'ui.bootstrap',                 // Ui Bootstrap
            'angulartics',
            'angulartics.google.analytics',
            "agGrid",
            "datatables",
            "oitozero.ngSweetAlert",
            "ngSanitize",
            "daterangepicker",
            "localytics.directives",
            "cgNotify",
            'ops.services.auth',
            'ops.services.user',
            'ops.views.base',
            'ops.views.reports',
            'ops.views.dashboard',
            'ops.views.bookings',
            'ops.views.editBookings',
            'ops.views.editBookingSummary',
            'ops.views.editBookingBilling',
            'ops.views.editBookingPickup',
            'ops.views.editBookingDoorstep',
            'ops.views.editBookingWorkshop',
            'ops.views.editBookingDocuments',
            'ops.views.editBookingDrop',
            'ops.views.editBookingCoupons',
            'ops.views.editBookingFeedback',
            'ops.views.editBookingNotifications',
            'ops.views.editBookingHistory',
            'ops.views.editPayment',
            'ops.views.users',
            'ops.views.userInquiry',
            'ops.views.editUserInquiry',
            'ops.views.createUserInquiry',
            'ops.views.editUser',
            'ops.views.editUserCar',
            'ops.views.changePassword',
            'ops.views.notifyUsers',
            'ops.views.createUsers',
            'ops.views.createUserCar',
            'ops.views.addPackage',
            'ops.views.workshops',
            'ops.views.recordings',
            'ops.views.alerts',
            'ops.views.raiseAlert',
            'ops.views.reportLiveWorkshop',
            'ops.views.scratchFinders',
            'ops.views.reportBookingFeedbackCustomer',
            'ops.views.reportBookingFeedbackOps',
            'ops.views.allLeads',
            'ops.views.crewDashboard',
            'ops.views.workshopScheduler',
            'ops.views.partDocs',
            'ops.views.partDocDetails'
        ])
            .constant('AUTH_EVENTS', {
                loginSuccess: 'auth-login-success',
                loginFailed: 'auth-login-failed',
                logoutSuccess: 'auth-logout-success',
                sessionTimeout: 'auth-session-timeout',
                notAuthenticated: 'auth-not-authenticated',
                notAuthorized: 'auth-not-authorized',
                serverError: 'server-error'
            })
            .constant('USER_ROLES', {
                all: '*',
                admin: 'admin',
                editor: 'editor',
                guest: 'guest'
            })
            .constant('BOOKING_EVENTS',{
                LoadFollowupBooking:'LoadFollowupBooking',
                LoadFollowupInquiry:'LoadFollowupInquiry'
            })
            .constant('COLOR_LIST', {
                pie: ['#B39DDB','#EF9A9A','#FFF59D','#A5D6A7','#9FA8DA','#F48FB1','#FFCC80','#EEEEEE','#80DEEA','#CE93D8',
                    '#FFE082', '#BCAAA4','#C5E1A5','#90CAF9','#FFAB91','#80CBC4','#E6EE9C','#B0BEC5','#81D4FA','#D81B60',
                    '#B71C1C','#1565C0','#2E7D32','#EF6C00','#6D4C41']
            })
            .factory('GlobalDataService', function() {
                var self = this;
                self.staticFileVersion = 100;
                return {
                    staticFileVersion : staticFileVersion,
                    getStaticFileVersion: function(){
                        return self.staticFileVersion;
                    },
                    setStaticFileVersion: function(v){
                        //console.log(v);
                        self.staticFileVersion = v;
                    }
                };
            })
            .filter('capitalize', function() {
                return function(input) {
                    return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
                };
            })
            .directive('capitalizeAll', function($parse) {
                return {
                    require: 'ngModel',
                    link: function(scope, element, attrs, modelCtrl) {
                        var capitalize = function(inputValue) {
                            if (inputValue === undefined) { inputValue = ''; }
                            var capitalized = inputValue.toUpperCase();
                            if(capitalized !== inputValue) {
                                modelCtrl.$setViewValue(capitalized);
                                modelCtrl.$render();
                            }
                            return capitalized;
                        };
                        modelCtrl.$parsers.push(capitalize);
                        capitalize($parse(attrs.ngModel)(scope)); // capitalize initial value
                    }
                };
            })
        ;
})();

