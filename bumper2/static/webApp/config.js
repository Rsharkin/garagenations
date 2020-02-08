/**
 * Created by inderjeet on 1/4/16.
 */
/**
 * Bumper
 *
 * Theme use AngularUI  outer to manage routing and views
 * Each view are defined as state.
 *
 */
var JSVersion = 'Version CONFIG_STATIC_FILE_UNIQUE_VERSION';
angular
    .module('bumper')
    .config ( config )
    .config(function($mdThemingProvider) {
        $mdThemingProvider.definePalette('bumper', {
            '50': '#ff6666',
            '100': '#ff6666',
            '200': '#ff6666',
            '300': '#ff6666',
            '400': '#ff6666',
            '500': '#ff6666',
            '600': '#ff6666',
            '700': '#ff6666',
            '800': '#ff6666',
            '900': '#ff6666',
            'A100': '#ff6666',
            'A200': '#ff6666',
            'A400': '#ff6666',
            'A700': '#ff6666',
            'contrastDefaultColor': 'light',    // whether, by default, text (contrast)
                                                // on this palette should be dark or light
            'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
                '200', '300', '400', 'A100'],
            'contrastLightColors': undefined    // could also specify this if default was 'dark'
        });
        $mdThemingProvider.definePalette('accentPalette',{
            '50': '#47289e',
            '100': '#47289e',
            '200': '#47289e',
            '300': '#47289e',
            '400': '#47289e',
            '500': '#47289e',
            '600': '#47289e',
            '700': '#47289e',
            '800': '#47289e',
            '900': '#47289e',
            'A100': '#47289e',
            'A200': '#47289e',
            'A400': '#47289e',
            'A700': '#47289e',
            'contrastDefaultColor': 'light',    // whether, by default, text (contrast)
                                                // on this palette should be dark or light
            'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
                '200', '300', '400', 'A100'],
            'contrastLightColors': undefined
        });
        $mdThemingProvider.theme('default').accentPalette('accentPalette');
        $mdThemingProvider.theme('default')
            .primaryPalette('bumper')
    })
    .config(function (LightboxProvider) {
        // set a custom template
        LightboxProvider.templateUrl = 'views/common/lightbox.html';
    })
    .config(function($sceDelegateProvider) {
        $sceDelegateProvider.resourceUrlWhitelist([
            // Allow same origin resource loads.
            'self',
            // Allow loading from our assets domain.  Notice the difference between * and **.
            //'http://srv*.assets.example.com/**'
            'https://telephony.ninjacrm.com/api/cdr/fetchRecordingFile.php**',
            'https://d1zpzoan72mtr9.cloudfront.net/**', // Staging CDN
            'https://d18qyvmj2t58jj.cloudfront.net/**', // Live CDN
            'https://staging.bumper.com/**',
            'https://bumper.com/**',
            'https://www.youtube.com/watch?v=QoCfrGcZk0A'
        ]);
    })
    .run(function($rootScope, $state, $templateCache, $location, $http, AUTH_EVENTS, $window, AuthService) {
        $rootScope.$state = $state;
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';

        $rootScope.$on(AUTH_EVENTS.notAuthenticated, function () {
            //console.log('notAuthenticated called.');
            // sweetAlert("Oops...", "You have been logged out. Please login again.", "warning");
            $window.localStorage.removeItem(AuthService.getJWTTokenName());
            window.location.href = '/';
        });
        $rootScope.$on(AUTH_EVENTS.logoutSuccess, function () {
            //console.log('Bye Bye!');
            window.location.href = '/';
        });
        $rootScope.$on(AUTH_EVENTS.notAuthorized, function () {
            //sweetAlert("Oops...", "You don't have permission to do this.", "warning");
        });
        $rootScope.$on(AUTH_EVENTS.serverError, function () {
            //sweetAlert("Oops...", "Failed on server. Please retry or contact dev team.", "error");
        });

        // Using data set title and Meta tags.
        $rootScope.$on('$stateChangeStart',
            function(event, toState, toParams, fromState, fromParams, options){
                var default_title = "Bumper.com  - India's First Network of Car Body Repair Garages";
                var default_keywords = "Car dent remover, car scratch remover, car painting, " +
                    "car paint touch up, car tinkering, car body repair, car repair, car garage," +
                    " car wash, Bumper, Car Bumper Repair, Car Painting cost in India, Car Denting " +
                    "Painting cost estimate, Car dent repair, car scratch repair, car dent removal," +
                    " car scratch removal, Full body car painting cost, Car dent puller, Car paint booth," +
                    " car Polishing, Car Cleaning, Car Panel Replacement, Car Parts Replacement";
                var default_desc = "Bumper.com is India's first network of auto body repair workshops." +
                    " Get high quality denting, painting and scratch removal work for your car at up to" +
                    " 60% less prices - from the comfort of your home.";
                $rootScope.seo_title = toState.data && toState.data.title? toState.data.title: default_title;
                $rootScope.seo_keywords = toState.data && toState.data.keywords? toState.data.keywords: default_keywords;
                $rootScope.seo_desc = toState.data && toState.data.desc? toState.data.desc: default_desc;

            });
    });

function config($stateProvider, $urlRouterProvider, $locationProvider, $httpProvider,
                $interpolateProvider) {

    $httpProvider.interceptors.push('AuthInterceptor');

    // To change the default angularjs symbol to not conflict.
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    $urlRouterProvider.otherwise("/");

    $locationProvider.html5Mode(true);
    var isDeviceMobile = false;
    if( navigator.userAgent.match(/Android/i)
        || navigator.userAgent.match(/webOS/i)
        || navigator.userAgent.match(/iPhone/i)
        || navigator.userAgent.match(/iPod/i)
        || navigator.userAgent.match(/BlackBerry/i)
        || navigator.userAgent.match(/Windows Phone/i)) {
        isDeviceMobile = true;
    }
    $stateProvider
        .state('base', {
            abstract: true,
            url: "",
            controller: 'BaseCtrl as base',
            templateUrl: 'views/new-templates/base.html',
            resolve: {
                init: function(AuthResolver) {
                    var user_id = jQuery('#baseUserId').val(); // TODO Check and remove
                    return AuthResolver.resolve();
                }
            }
        })
        .state('base.home',{
            url: "/",
            views: {
                '@base': {
                    templateUrl:  function () {
                        if(isDeviceMobile){
                            return 'views/new-templates/home-mobile.html';
                        } else {
                            return 'views/new-templates/home.html';
                        }
                    },
                    controller: 'BaseCtrl as base'
                },
                'secondFold@base.home': {
                    templateUrl:  function () {
                        if(isDeviceMobile){
                            return 'views/new-templates/second-fold-mobile.html';
                        } else {
                            return 'views/new-templates/second-fold.html';
                        }
                    },
                    controller: 'BaseCtrl as base'
                }
            },
            data: {
                title: "Bumper.com  - India's First Network of Car Body Repair Garages",
                keywords: "Car dent remover, car scratch remover, car painting," +
                " car paint touch up, car tinkering, car body repair, " +
                "car repair, car garage, car wash, Bumper, Car Bumper Repair," +
                " Car Painting cost in India, Car Denting Painting cost estimate," +
                " Car dent repair, car scratch repair, car dent removal, car scratch removal, " +
                "Full body car painting cost, Car dent puller, Car paint booth, car Polishing," +
                " Car Cleaning, Car Panel Replacement, Car Parts Replacement",
                desc: "Bumper.com is India's first network of auto body repair workshops. " +
                "Get high quality denting, painting and scratch removal work for your car at " +
                "up to 60% less prices - from the comfort of your home."
            }
        })
        .state('base.estimator', {
            url: "/car-dent-paint-body-repair-cost/",
            views: {
                '@base': {
                    controller: 'CarPanelSearchController as carPanelSearchCtrl',
                    templateUrl: 'views/new-templates/panels.html'
                }
            },
            data: {
                title: "Car Denting & Painting Repair - Cost Estimator | Bumper.com",
                keywords: "Car Dent remover, Car Scratch remover, Car Painting," +
                " Car denting Painting,Car Denting & Painting charges," +
                " Car Painting Cost Estimate, Car Painting Cost in India," +
                " Car Scratch repair cost India, Car Paintig cost Bangalore," +
                " Car Repair Estimate, Full Car Painting Cost, Full Body Car Paint," +
                " Car Paint Warranty, Car Parts Replacement- Headlight, Taillight, " +
                "Windshield, Fog Lamp, Side View Mirror, Number Plate, Front Logo, " +
                "Car Repainting, Car color change, Car Panel Repair- Front Bumper," +
                " Rear Bumper, Fender, Quarter Panel, Front Door, Rear door, Dikky, " +
                "Bonnet, Running Board, Multi Brand Car Bodyshop - Maruti, Hyundai, Honda," +
                " Ford, Skoda, Volkswagen, Toyota, Renault, Tata, Nissan, Chevrolet, Fiat," +
                " Mahindra, Audi, BMW, Mercedes, Jaguar",
                desc: "Bumper.com cost estimator gives an estimate of expenditure for Car dent " +
                "removal and Car scratch removal. Get the estimate for the work on your " +
                "car from the comfort of your home."
            },
        })
        .state('base.package', {
            url: "/car-wash/",
            views: {
                '@base': {
                    controller: 'PackagesController as packagesController',
                    templateUrl: 'views/new-templates/package.html'
                }
            },
            data: {
                title: "Car Wash and Cleaning Services - Bumper.com",
                keywords: "Car Wash, Car Wash near me, Car Washing Bangalore," +
                "Car Cleaning, Car Windshield Polish, Car AC Disinfection, " +
                "Car AC duct cleaning, Car Polishing, Car Spa, Car Detailing, " +
                "Car Vacuum Cleaning, Car Seats Cleaning, Car Dashboard Polish, " +
                "Car Tyre Polish, Car Interior & Exterior Cleaning, Car Glass Cleaner",
                desc: "Get your car cleaned and washed at your doorstep with Bumper.com" +
                " Car wash and Cleaning services, choose from a variety of services " +
                "including Complete Interior- extrior Detailing & Paint protection."
            }
        })
        .state('base.cart', {
            url: "/cart/",
            views: {
                '@base': {
                    controller: "CartController as cartCtrl",
                    templateUrl: 'views/new-templates/cart.html'
                }
            }
        })
        .state('base.schedule', {
            url: "/schedule/:scheduleFor/",
            views: {
                '@base': {
                    controller: "ScheduleController as scheduleCtrl",
                    templateUrl: function () {
                        if(isDeviceMobile) {
                            return 'views/new-templates/schedule-mobile.html'
                        } else {
                            return 'views/new-templates/schedule.html';
                        }

                    }
                },
                resolve: {
                    scheduleFor: function ($stateParams) {
                        return $stateParams.scheduleFor? $stateParams.scheduleFor: 'pickup';
                    }
                }
            }
        })
        .state('base.status', {
            url: "/booking-status/",
            views: {
                '@base': {
                    controller: "StatusController as statusCtrl",
                    templateUrl: 'views/new-templates/status.html'
                }
            }
        })
        .state('base.payment', {
            url: "/payment/",
            views: {
                '@base': {
                    controller: "PaymentController as paymentCtrl",
                    templateUrl: 'views/new-templates/payment.html'
                }
            }
        })
        .state('base.about', {
            url: "/about-us/",
            views: {
                '@base': {
                    templateUrl: 'views/common/about.html'
                }
            },
            data:{
                title:"Bumper.com - India's First Network of Car Body Repair Garages",
                keywords:"Car Care, Bumper, Car Dent remover, Car Scratch remover," +
                " Car Painting, Car Wash, Car Cleaning, Car Polishing, Car Tinkering,Car Lovers",
                desc:"Bumper.com is India's first network of auto body repair workshops." +
                " Get high quality denting, painting and scratch removal work for your" +
                " car at up to 60% less prices - from the comfort of your home."
            }
        })
        .state('base.contact', {
            url: "/help/",
            views: {
                '@base': {
                    templateUrl: 'views/common/contact.html',
                    controller: function helpController($location,$anchorScroll) {
                        $location.hash('headerTop');
                        $anchorScroll();
                    }
                }
            },
            data:{
                title:"Frequently Asked Questions - Bumper.com",
                keywords:"Car Dent Remover, Car Scratch Remover, Car Painting," +
                " Bumper.com - Car Workshop Locations, Car Paint Matching, Car Paint Warranty, " +
                "Car Parts replacement, Car Panel Replacement, Car Pickup Drop",
                desc:"Here are some frequently asked questions on Car dent Removal and Car scratch removal."
            }
        })
        .state('base.contactUs', {
            url: "/contact-us/",
            views: {
                '@base': {
                    templateUrl: 'views/common/contact-us.html',
                    controller: 'ContactController as contactCtrl'
                }
            },
            data:{
                title:"Car Garage & Workshop Locations - Bumper.com",
                keywords:"Car Garage, Car Wokshop, Car Bodyshop," +
                " Car Bodywork repair, Car Mechanic, Car Body Repair," +
                " Bumper.com Bodyshops Garages - Whitefield, Horamavu," +
                " Kudlu Gate, Atiibele, Hosur Road, Rajaji Nagar," +
                " Dommasandra, Koramangala, Car Dent remover, " +
                "Car Scratch remover, Car Painting, Car Dent repair, " +
                "car Scratch repair, Car Repair centre",
                desc:"Bumper.com bodyshop Garages are located at Whitefield," +
                " Horamavu, Kudlu Gate, Atiibele, Hosur Road," +
                "Rajaji Nagar, Dommasandra & Koramangala in Bangalore City."
            }
        })
        .state('base.dentOrScratch', {
            url: "/car-dent-scratch-remover/",
            views: {
                '@base': {
                    templateUrl: 'views/new-templates/dent-scratch-def.html',
                    controller: function dentScratchController($location, $anchorScroll) {
                        var old = $location.hash();
                        $location.hash('headerTop');
                        $anchorScroll();
                        $location.hash(old);
                        $(document).ready(function () {
                            $("#owl-demo").owlCarousel({
                                navigation : true, // Show next and prev buttons
                                slideSpeed : 300,
                                paginationSpeed : 400,
                                singleItem: true

                            });
                        })
                    }
                }
            },
            data:{
                title:"Dent Free Scratch Free Car - Bumper.com",
                keywords:"Car dent remover, car scratch remover, " +
                "car painting, car paint touch up, car tinkering," +
                " car body repair, Bumper, Car Bumper Repair, " +
                "Car Painting cost in India, Car Denting Painting cost estimate," +
                " Car dent repair, car scratch repair, car dent removal," +
                " car scratch removal, Full body car painting cost, Car dent puller," +
                " Car paint booth, Car Putty, Car Polishing",
                desc:"Bumper.com gives you a chance to own a dent free scratch free" +
                " car with their Car dent removal and Car scratch removal services" +
                " at 60% lesser cost than the marketplace."
            }
        })
        .state('base.razorPay',{
            url:"/razorpay-success/",
            views:{
                '@base':{
                    templateUrl:'views/common/razorpay-success.html',
                    controller:'RazorPayController as razorPayCtrl'
                }
            },
            params:{
                'bookingId':null,
                'amount':null
            }
        })
        .state('base.workshop',{
            url:"/workshop-network/",
            views:{
                '@base':{
                    templateUrl:'views/common/workshop-section-mobile.html',
                    controller:'BaseCtrl as base'
                }
            }
        })
        .state('base.howItWorks',{
            url:"/how-it-works/",
            views:{
                '@base':{
                    templateUrl:'views/common/how-it-works-mobile.html'
                }
            }
        })
        .state('base.beforeAfter',{
            url:"/before-after/",
            views:{
                '@base':{
                    templateUrl:'views/common/before-after.html',
                    controller: function beforeAfterController($location, $anchorScroll) {
                        var old = $location.hash();
                        $location.hash('headerTop');
                        $anchorScroll();
                        $location.hash(old);
                    }
                }
            }
        })
        .state('base.customerReviews',{
            url:"/customer-reviews/",
            views:{
                '@base':{
                    templateUrl:'views/new-templates/customer-reviews.html',
                    controller: 'customerReviewController as crCtrl'
                }
            },
            data:{
                title:"Bumper.com Reviews, Feedback, Customer Testimonials - Bumper.com",
                keywords:"Bumper.com user review, Feedback, Bumper.com Customer testimonials," +
                " Bumper.com Customer reviews, Car Dent remover, Car Scratch remover, Car Painting," +
                " Car Dent Repair, Car Scratch Repair, Car Wash, Car Cleaning, Car Polishing," +
                " Car Painting cost in India",
                desc:"This is a user review of the services of Bumper.com. The Car dent removal," +
                " Car scratch removal and car painting have been reviewed by users who have used them." +
                " Here are some customer feedback."
            }
        })
        .state('base.paymentWithoutLogin',{
            url:"/direct-payment/",
            views:{
                '@base':{
                    templateUrl:'views/new-templates/payment-template.html',
                    controller: 'directPaymentController as directPayCtrl'
                }
            }
        })
        .state('base.privacy',{
            url:"/privacy-policy/",
            views:{
                '@base':{
                    templateUrl:'views/common/privacy.html',
                    controller: 'privacyController as privacyCtrl'
                }
            }
        })
        .state('base.inventory',{
            url:"/inventory-list/",
            views:{
                '@base':{
                    templateUrl:'views/common/inventory-list.html',
                    controller: 'ChecklistController as checklistCtrl'
                }
            }
        })
        .state('base.electrical',{
            url:"/electrical-list/",
            views:{
                '@base':{
                    templateUrl:'views/common/electrical-list.html',
                    controller: 'ChecklistController as checklistCtrl'
                }
            }
        })
        .state('base.whatsNext',{
            url:"/whats-next/",
            views:{
                '@base':{
                    templateUrl:'views/common/whats-next.html',
                    controller: 'ChecklistController as checklistCtrl'
                }
            }
        })
        .state('base.feedback', {
            url: "/feedback/",
            views: {
                '@base': {
                    templateUrl: 'views/common/feedback.html',
                    controller: 'FeedbackController as feedbackCtrl'
                }
            }
        })
        .state('base.referral', {
            url: '/referral/',
            views: {
                '@base': {
                    templateUrl: 'views/common/referral.html',
                    controller: 'ReferralController as refCtrl'
                }
            }
        })
        .state('base.carPhotos', {
            url: "/car-photos/",
            views: {
                '@base': {
                    templateUrl: 'views/common/car-photos.html',
                    controller: 'ChecklistController as checklistCtrl'
                }
            }
        })
    ;
}
