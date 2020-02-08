
angular.module('bumper.services.user',[
])
    .service('UserService', function($http, $window, AuthService){
        var self = this,
            current_user = null,
            URLS={
                USER_LOGOUT: '/core/logout/',
                REQ_LOGIN_OTP: '/api/user/send_login_code/',
                OTP_SIGNUP: '/api/user/send_signup_code/',
                SOCIAL_SIGNUP: '/api/user/',
            };

        self.setCurrentUser = function(user_obj){
            if(user_obj){

                //console.log('inside current user',user_obj);
                current_user = user_obj;
            }
        };

        self.getCurrentUser = function(){
            return current_user;
        };
        self.changeUserCity = function (city) {
            var data = {
                "city_id":city
            };
            var user = self.getCurrentUser();
            return $http.patch(URLS.SOCIAL_SIGNUP+user.id+"/",data);
        };

        self.socialLogin = function(provider, access_token) {
            return $http({
                method:'POST',
                url: URLS.SOCIAL_SIGNUP,
                data:{
                    provider: provider,
                    access_token: access_token
                },
                skipAuthorization: true
            });
            // return $http.post(URLS.SOCIAL_SIGNUP, {
            //     provider: provider,
            //     access_token: access_token
            // })
        };

        self.requestLoginOtp = function(phone) {
            return $http.post(URLS.REQ_LOGIN_OTP, {
                phone: phone
            })
        };

        self.login_validate_errors = function(phone, auth_code) {
            return $http.post('/api/user/validate_auth_code/', {
                auth_code: auth_code,
                phone: phone
            })
        };

        self.otpSignup = function(user_details) {
            /*
             * Required name, email, phone, device_type = web, city_id,
             * not required but needed utm_source, utm_medium, utm_campaign
             * */
            return $http.post(URLS.OTP_SIGNUP, user_details)
        };

        self.logout = function() {
            $window.localStorage.removeItem(AuthService.getJWTTokenName());
            return $http.post(URLS.USER_LOGOUT, {
                redirect_field_name: '/login/'
            });
        };

    })
;