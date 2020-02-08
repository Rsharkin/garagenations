/**
 * MainCtrl - controller
 * Contains several global data used in different view
 *
 */
angular
    .module('ops')
    .controller('MainCtrl', function MainCtrl($rootScope,$scope, BookingService, notify) {
        var self = this;


        // Handle incoming messages. Called when:
        // - a message is received while the app has focus
        // - the user clicks on an app notification created by a sevice worker
        //   `messaging.setBackgroundMessageHandler` handler.
        messaging.onMessage(function(payload) {
            console.log("Message received in foreground: ", payload);
        notify({
            message: payload.notification.body,
            classes: 'alert-info',
            position: 'right',
            duration: 50000,
            //templateUrl: 'views/common/notify.html',
            messageTemplate: '<span><div><b>'+payload.notification.title+'</b><div>'+payload.notification.body+' <a href="/core/bookings/editBooking/'+payload.data.booking_id+'/" target="_blank">details</a></div></div></span>'
        });
            // ...
        });
    })
;


