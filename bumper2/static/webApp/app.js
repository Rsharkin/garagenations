/**
 * Created by inderjeet on 1/4/16.
 */
/**
 * Bumper Website
 *
 */
; (function () {
    var app = angular.module('bumper', [
            'ui.router',                    // Routing
            'ui.bootstrap',                 // Ui Bootstrap
            'satellizer',
            'ngMaterial',
            'ngAnimate',
            'ngSanitize',
            'angulartics',
            'angulartics.google.analytics',
            //'angulartics.localytics',
            'bumper.services.auth',
            'bumper.services.user',
            'bumper.view.base',
            'bumper.services.data',
            'bumper.view.carSearch',
            'bumper.view.packages',
            'bumper.view.cart',
            'bumper.view.schedule',
            'bumper.view.status',
            'bumper.view.status',
            'bumper.view.contact',
            'bumper.view.payment',
            'bumper.view.razorpay',
            'updateMeta',
            'ngMessages',
            'bootstrapLightbox',
            'bumper.view.customer',
            'bumper.view.directPayment',
            'bumper.view.customer',
            'bumper.view.privacy',
            'bumper.view.feedback',
            'bumper.view.checklist',
            'bumper.view.referral'
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
            .constant('BUMPER_EVENTS', {
                BookingChanged: 'BookingChanged',
                SelectedCarModelChanged: 'SelectedCarModelChanged',
                SelectedCarModelParams: 'SelectedCarModelParams',
                UserUpdated: 'UserUpdated',
                BookingUpdated: 'booking updated',
                StepUpdated: 'step updated',
                LoginRequired: 'login Required',
                ChatLoaded: 'chatloaded',
                CityUpdated:'CityUdated',
                cityBangalore: 'cityBangalore',
                cityDelhi:'cityDelhi'
            })
            .constant('USER_ROLES', {
                all: '*',
                admin: 'admin',
                editor: 'editor',
                guest: 'guest'
            })
            .constant('COLOR_LIST', {
                pie: ['#B39DDB','#EF9A9A','#FFF59D','#A5D6A7','#9FA8DA','#F48FB1','#FFCC80','#EEEEEE','#80DEEA','#CE93D8',
                    '#FFE082', '#BCAAA4','#C5E1A5','#90CAF9','#FFAB91','#80CBC4','#E6EE9C','#B0BEC5','#81D4FA','#D81B60',
                    '#B71C1C','#1565C0','#2E7D32','#EF6C00','#6D4C41']
            })
            .filter('capitalize', function() {
                return function(input) {
                    return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
                }
            })
            .filter('html',function($sce){
                return function(input){
                    return $sce.trustAsHtml(input);
                }
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

