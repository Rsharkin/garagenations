/**
 * Created by Indy on 23/03/17.
 */
    // Initialize Firebase
var config = {
        messagingSenderId: "880205711592"
    };

firebase.initializeApp(config);
// Retrieve Firebase Messaging object.
const messaging = firebase.messaging();

// Get Instance ID token. Initially this makes a network call, once retrieved
// subsequent calls to getToken will return from cache.
function getInstanceIdToken(){
    messaging.getToken()
        .then(function(currentToken) {
            if (currentToken) {
                sendTokenToServer(currentToken);
            } else {
                // Show permission request.
                console.log('No Instance ID token available. Request permission to generate one.');
                // Show permission UI.
                requestPerm();
            }
        })
        .catch(function(err) {
            console.log('An error occurred while retrieving token. ', err);
        });
}

// Callback fired if Instance ID token is updated.
messaging.onTokenRefresh(function() {
    messaging.getToken()
        .then(function(refreshedToken) {
            console.log('Token refreshed.');
            // Indicate that the new Instance ID token has not yet been sent to the
            // app server.
            // Send Instance ID token to app server.
            sendTokenToServer(refreshedToken);
        })
        .catch(function(err) {
            console.log('Unable to retrieve refreshed token ', err);
        });
});

function requestPerm(){
    messaging.requestPermission()
        .then(function() {
            //console.log('Notification permission granted.');
            getInstanceIdToken();
        })
        .catch(function(err) {
            console.log('Unable to get permission to notify.', err);
        });
}

// [END background_handler]
function sendTokenToServer(token){
    //console.log('Token received, saving to local storage:', token);
    window.localStorage[window.location.hostname+'fcmToken'] = token;
    var userId = $('#baseUserId').val();
    $.ajax({
        url: '/api/user/'+ userId +'/get_user_profile_with_token/',
        success: function(result){
            //console.log('user details', result);
            var jwtToken = result.token;
            var data = {
                'registration_id': token,
                'device_info': 'web-browser - ops panel',
                'device_type': 'web',
                'is_fcm': true
            };

            $.ajax({
                url: '/api/user/send_reg_details/',
                data: data,
                method: 'POST',
                beforeSend: function (xhr) {
                    /* Authorization header */
                    xhr.setRequestHeader("Authorization", "JWT " + jwtToken);
                    xhr.setRequestHeader("source", "opsPanel");
                },
                success: function(result){
                    //console.log('user device details', result);
                }
            });
        }
    });
}

navigator.serviceWorker.register('firebase/firebase-messaging-sw.js')
    .then(function(registration){
        messaging.useServiceWorker(registration);
        getInstanceIdToken();
    });