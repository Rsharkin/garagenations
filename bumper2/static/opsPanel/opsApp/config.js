/**
 * Created by inderjeet on 1/4/16.
 */
/**
 * ops
 *
 * Theme use AngularUI Router to manage routing and views
 * Each view are defined as state.
 *
 */
// this variable is here to burst cache for JS file's minified version.
var JSVersion = 'Version CONFIG_STATIC_FILE_UNIQUE_VERSION';
angular
    .module('ops')
    .config(config)
    .config(function($sceDelegateProvider) {
        $sceDelegateProvider.resourceUrlWhitelist([
            // Allow same origin resource loads.
            'self',
            // Allow loading from our assets domain.  Notice the difference between * and **.
            //'http://srv*.assets.example.com/**'
            'https://telephony.ninjacrm.com/api/cdr/fetchRecordingFile.php**',
            'https://d1rqvon388p25n.cloudfront.net/**'
        ]);
    })
    .run(function($rootScope, $state, $templateCache, $location, $http, AUTH_EVENTS) {
        $rootScope.$state = $state;
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';

        $rootScope.$on(AUTH_EVENTS.notAuthenticated, function () {
            //console.log('notAuthenticated called.');
            sweetAlert("Oops...", "You have been logged out. Please login again.", "warning");
            window.location.href = '/core/login/';
        });

        $rootScope.$on(AUTH_EVENTS.logoutSuccess, function () {
            //console.log('Bye Bye!');
            window.location.href = '/core/login/';
        });

        $rootScope.$on(AUTH_EVENTS.notAuthorized, function () {
            sweetAlert("Oops...", "You don't have permission to do this.", "warning");
        });

        $rootScope.$on(AUTH_EVENTS.serverError, function () {
            sweetAlert("Oops...", "Failed on server. Please retry or contact dev team.", "error");
        });
    });

function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider, $locationProvider, $httpProvider,
                $interpolateProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');

    // To change the default angularjs symbol to not conflict.
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    $urlRouterProvider.otherwise("/bookings/");

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });
    $locationProvider.html5Mode(true);

    $stateProvider
        .state('base', {
            abstract: true,
            url: "",
            controller: 'BaseCtrl as baseCtrl',
            templateUrl: "views/common/content-top-navigation.html",
            resolve: {
                init: function(AuthResolver, GlobalDataService) {
                    var user_id = jQuery('#baseUserId').val();
                    var staticVersion = jQuery('#staticFileVersion').val();
                    GlobalDataService.setStaticFileVersion(staticVersion);
                    return AuthResolver.resolve(user_id);
                }
            }
        })
        .state('base.dashboard', {
            url: "/",
            views: {
                '@base': {
                    templateUrl: 'views/dashboard.html'
                },
                'report_workshop_live@base.dashboard': {
                    controller: 'ReportWorkshopLiveCtrl as reportWorkshopLiveCtrl',
                    templateUrl: 'views/report-workshop-live.html'
                }
            }
        })
        .state('base.workshopScheduler',{
            url: '/ws-scheduler/',
            views:{
                '@base': {
                    controller: 'WSCtrl as wsCtrl',
                    templateUrl: 'views/workshop-scheduler.html'
                }
            }
        })
        .state('base.crewDashboard',{
            url: '/crew-dashboard/',
            views:{
                '@base': {
                    controller: 'CrewDashCtrl as crewDashCtrl',
                    templateUrl: 'views/dashboard-crew.html'
                }
            }
        })
        .state('base.userInquiry', {
            url: "/user-inquiry/",
            views: {
                '': {
                    controller: 'UserInquiryCtrl as userInquiryCtrl',
                    templateUrl: 'views/user-inquiry.html'
                }
            }
        })
        .state('base.userInquiry.editUserInquiry', {
            url: "edit-inquiry/:userInquiryId/",
            views: {
                '@base': {
                    controller: 'EditUserInquiryCtrl as editUserInquiryCtrl',
                    templateUrl: 'views/edit-user-inquiry.html'
                }
            }
        })
        .state('base.userInquiry.CreateUserInquiry', {
            url: "create-inquiry/:userId/",
            views: {
                '@base': {
                    controller: 'CreateUserInquiryCtrl as createUserInquiryCtrl',
                    templateUrl: 'views/create-user-inquiry.html'
                }
            }
        })
        .state('base.workshops', {
            url: "/workshops/",
            views: {
                '': {
                    controller: 'WorkshopsCtrl as workshopsCtrl',
                    templateUrl: 'views/workshops.html'
                }
            }
        })
        .state('base.recordings', {
            url: "/recordings/:phoneNumbers/",
            views: {
                '': {
                    controller: 'RecordingsCtrl as recordingsCtrl',
                    templateUrl: 'views/recordings.html'
                }
            }
        })
        .state('base.partDocs', {
            url: "/part-docs/",
            views: {
                '': {
                    controller: 'PartDocsCtrl as partDocsCtrl',
                    templateUrl: 'views/part-documents.html'
                }
            }
        })
        .state('base.partDocs.details', {
            url: "details/:bookingId/:partDocId/",
            views: {
                '@base': {
                    controller: 'PartDocDetailsCtrl as partDocDetailsCtrl',
                    templateUrl: 'views/part-doc-details.html'
                }
            }
        })
        .state('base.bookings', {
            url: "/bookings/",
            views: {
                '': {
                    controller: 'BookingCtrl as bookingCtrl',
                    templateUrl: 'views/booking.html'
                }
            }
        })
        .state('base.bookings.editBooking', {
            url: "editBooking/:bookingId/",
            views: {
                '@base': {
                    controller: 'EditBookingCtrl as editBookingCtrl',
                    templateUrl: 'views/edit-booking.html'
                }
            },
            resolve: {
                booking: function($stateParams, BookingService, $window) {
                    var bookingId = $stateParams.bookingId;
                    return BookingService.getBookingById(bookingId)
                        .then(function (data) {
                            BookingService.setCurrentBooking(data);
                            //console.log('Booking->', data);
                            return data;
                        });
                }
            },
            data: {
                pageTitle: 'Edit Booking'
            }
        })
        .state('base.bookings.editBooking.summary', {
            url: "summary/",
            views: {
                'summary@base.bookings.editBooking': {
                    controller: 'EditBookingSummaryCtrl as editBookingSummaryCtrl',
                    templateUrl: 'views/edit-booking-summary.html'
                }
            }
        })
        .state('base.bookings.editBooking.doorstep', {
            url: "doorstep/",
            views: {
                'doorstep@base.bookings.editBooking': {
                    controller: 'EditBookingDoorstepCtrl as editBookingDoorstepCtrl',
                    templateUrl: 'views/edit-booking-doorstep.html'
                }
            }
        })
        .state('base.bookings.editBooking.pickup', {
            url: "pickup/",
            views: {
                'pickup@base.bookings.editBooking': {
                    controller: 'EditBookingPickupCtrl as editBookingPickupCtrl',
                    templateUrl: 'views/edit-booking-pickup.html'
                }
            }
        })
        .state('base.bookings.editBooking.workshop', {
            url: "workshop/",
            views: {
                'workshop@base.bookings.editBooking': {
                    controller: 'EditBookingWorkshopCtrl as editBookingWorkshopCtrl',
                    templateUrl: 'views/edit-booking-workshop.html'
                }
            }
        })
        .state('base.bookings.editBooking.drop', {
            url: "drop/",
            views: {
                'drop@base.bookings.editBooking': {
                    controller: 'EditBookingDropCtrl as editBookingDropCtrl',
                    templateUrl: 'views/edit-booking-drop.html'
                }
            }
        })
        .state('base.bookings.editBooking.billing', {
            url: "billing/",
            views: {
                'billing@base.bookings.editBooking': {
                    controller: 'EditBookingBillingCtrl as editBookingBillingCtrl',
                    templateUrl: 'views/edit-booking-billing.html'
                }
            }
        })
        .state('base.bookings.editBooking.addPayment',{
            url: "add-payment/",
            views:{
                '@base':{
                    controller: 'EditPaymentCtrl as editPaymentCtrl',
                    templateUrl: 'views/edit-payment.html'
                }
            }
        })
        .state('base.bookings.editBooking.addRefund',{
            url: "add-refund/",
            views:{
                '@base':{
                    controller: 'EditPaymentCtrl as editPaymentCtrl',
                    templateUrl: 'views/add-refund.html'
                }
            }
        })
        .state('base.bookings.editBooking.editPayment', {
            url: "edit-payment/:paymentId/",
            views:{
                '@base':{
                    controller: 'EditPaymentCtrl as editPaymentCtrl',
                    templateUrl: 'views/edit-payment.html'
                }
            }
        })
        .state('base.bookings.editBooking.documents', {
            url: "documents/",
            views: {
                'documents@base.bookings.editBooking': {
                    controller: 'EditBookingDocumentCtrl as editBookingDocumentCtrl',
                    templateUrl: 'views/edit-booking-documents.html'
                }
            }
        })
        .state('base.bookings.editBooking.pickupJobCard', {
            url: "pickupJobCard/",
            views: {
                'pickupJobCard@base.bookings.editBooking': {
                    controller: 'UsersCtrl as usersCtrl',
                    templateUrl: 'views/users.html'
                }
            }
        })
        .state('base.bookings.editBooking.coupons', {
            url: "coupons/",
            views: {
                'coupons@base.bookings.editBooking': {
                    controller: 'EditBookingCouponCtrl as editBookingCouponCtrl',
                    templateUrl: 'views/edit-booking-coupons.html'
                }
            }
        })
        .state('base.bookings.editBooking.feedback', {
            url: "feedback/",
            views: {
                'feedback@base.bookings.editBooking': {
                    controller: 'EditBookingFeedbackCtrl as editBookingFeedbackCtrl',
                    templateUrl: 'views/edit-booking-feedback.html'
                }
            }
        })
        .state('base.bookings.editBooking.notifications', {
            url: "notifications/",
            views: {
                'notifications@base.bookings.editBooking': {
                    controller: 'EditBookingNotificationCtrl as editBookingNotificationCtrl',
                    templateUrl: 'views/edit-booking-notifications.html'
                }
            }
        })
        .state('base.bookings.editBooking.history', {
            url: "history/",
            views: {
                'history@base.bookings.editBooking': {
                    controller: 'EditBookingHistoryCtrl as editBookingHistoryCtrl',
                    templateUrl: 'views/edit-booking-history.html'
                }
            }
        })
        .state('base.createUser', {
            url: "/create-user/:flow/",
            views: {
                '@base': {
                    controller: 'CreateUserController as createUserCtrl',
                    templateUrl: 'views/create-user.html'
                }
            }
        })
        .state('base.createUser.addUserCar', {
            url: "add-user-car/",
            views: {
                'contentView@base.createUser': {
                    controller: 'UserCarController as userCarCtrl',
                    templateUrl: 'views/add-car.html'
                }
            }
        })
        .state('base.createUser.addPackage', {
            url: "add-package/",
            views: {
                'contentView@base.createUser': {
                    controller: 'AddPackageController as addPackageCtrl',
                    templateUrl: 'views/add-package.html'
                }
            }
        })
        .state('base.users', {
            url: "/users/",
            views: {
                '': {
                    controller: 'UsersCtrl as usersCtrl',
                    templateUrl: 'views/users.html'
                }
            }
        })
        .state('base.users.editUser', {
            url: "edit-user/:userId/",
            views: {
                '@base': {
                    controller: 'EditUserCtrl as editUserCtrl',
                    templateUrl: 'views/edit-user.html'
                }
            }
        })
        .state('base.users.editUserCar', {
            url: "edit-user-car/:userCarId/",
            views: {
                '@base': {
                    controller: 'EditUserCarCtrl as editUserCarCtrl',
                    templateUrl: 'views/edit-user-car.html'
                }
            }
        })
        .state('base.reports', {
            url: "/reports/",
            views: {
                '': {
                    templateUrl: 'views/reports.html'
                }
            }
        })
        .state('base.reports.feedback',{
            url: "feedback/",
            views: {
                'feedback@base.reports':{
                    templateUrl: 'views/report-booking-feedback.html'
                }
            }
        })
        .state('base.reports.feedback.customer',{
            url: "customer/",
            views: {
                'customer@base.reports.feedback': {
                    controller: "ReportBookingFeedbackCustCtrl as custFeedbackCtrl",
                    templateUrl: "views/report-booking-feedback-customer.html"
                }
            }
        })
        .state('base.reports.feedback.ops',{
            url: "ops/",
            views: {
                'ops@base.reports.feedback': {
                    controller: "ReportBookingFeedbackOpsCtrl as opsFeedbackCtrl",
                    templateUrl: "views/report-booking-feedback-ops.html"
                }
            }
        })
        .state('base.reports.followups', {
            url: "followups/",
            views: {
                'followups@base.reports': {
                    templateUrl: 'views/report-followups.html'
                }
            }
        })
        .state('base.reports.followups.bookings', {
            url: "bookings/",
            views: {
                'bookings@base.reports.followups': {
                    controller: 'ReportBookingFollowupsCtrl as reportBookingFollowupsCtrl',
                    templateUrl: 'views/report-booking-followup.html'
                }
            }
        })
        .state('base.reports.followups.inquiry', {
            url: "inquiry/",
            views: {
                'inquiry@base.reports.followups': {
                    controller: 'ReportInquiryFollowupsCtrl as reportInquiryFollowupsCtrl',
                    templateUrl: 'views/report-inquiry-followup.html'
                }
            }
        })
        .state('base.reports.crew', {
            url: "crew/",
            views:{
                'crew@base.reports':{
                    controller: 'ReportCrewCtrl as reportCrewCtrl',
                    templateUrl: 'views/report-crew.html'
                }
            }
        })
        .state('base.alerts', {
            url: "/alerts/",
            views: {
                '': {
                    controller: 'AlertsCtrl as alertsCtrl',
                    templateUrl: 'views/alerts.html'
                }
            }
        })
        .state('base.alerts.raiseAlert', {
            url: "raise-alert/",
            views: {
                '@base': {
                    controller: 'RaiseAlertCtrl as raiseAlertCtrl',
                    templateUrl: 'views/add-alert.html'
                }
            }
        })
        .state('base.notifyUsers', {
            url: "/notify-users/",
            views: {
                '': {
                    controller: 'NotifyUsersCtrl as notifyUsersCtrl',
                    templateUrl: 'views/notify-users.html'
                }
            }
        })
        .state('base.changePassword', {
            url: "/change-password/",
            views: {
                '': {
                    controller: 'ChangePassCtrl as changePassCtrl',
                    templateUrl: 'views/change-password.html'
                }
            }
        })
        .state('base.campaigns',{
            url: "/campaigns/",
            views: {
                '': {
                    templateUrl: "views/campaigns.html"
                }
            }
        })
        .state('base.campaigns.scratchFinders',{
            url:"scratch-finders/",
            views:{
                'scratchFinders@base.campaigns':{
                    controller: "ScratchFindersCtrl as scratchFindersCtrl",
                    templateUrl: "views/scratch-finders.html"
                }
            }
        })
        .state('base.campaigns.allLeads',{
            url: 'all-leads/',
            views: {
                'allLeads@base.campaigns':{
                    controller: "AllLeadsCtrl as allLeadsCtrl",
                    templateUrl: "views/all-leads.html"
                }
            }
        })
    ;
}


