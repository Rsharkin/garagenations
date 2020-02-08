
angular.module('bumper.services.auth',[
])
    .service('AuthService', function($window, $location){
        var self = this;

        self.source = 'web';
        self.feedbackToken = null;

        self.saveFeedbackToken =function (token) {
            self.feedbackToken = token;
        };

        self.getJWTTokenName = function () {
            return $location.host() + 'WebJWTToken';
        };

        self.parseJwt = function(token) {
            var base64Url = token.split('.')[1];
            var base64 = base64Url.replace('-', '+').replace('_', '/');
            return JSON.parse($window.atob(base64));
        };

        self.saveToken = function(token) {
            $window.localStorage[self.getJWTTokenName()] = token;
        };

        self.getToken = function() {
            return $window.localStorage[self.getJWTTokenName()];
        };
        self.getFeedbackToken = function () {
            return self.feedbackToken;
        };

        self.isAuthenticated = function() {
            var token = self.getToken();
            if(token) {
                var params = self.parseJwt(token);
                return Math.round(new Date().getTime() / 1000) <= params.exp;
            } else {
                return false;
            }
        };

        self.setSource = function(){
            if(navigator.userAgent.match(/iPhone/i)
                || navigator.userAgent.match(/iPad/i)
                || navigator.userAgent.match(/iPod/i)
                || navigator.userAgent.match(/Android/i)
                || navigator.userAgent.match(/webOS/i)
                || navigator.userAgent.match(/BlackBerry/i)
                || navigator.userAgent.match(/Windows Phone/i)) {
                self.source = 'mobile-web';
            }else{
                self.source = 'desktop-web';
            }
        }
    })
    .factory('AuthInterceptor', function ($rootScope, $q, AUTH_EVENTS, AuthService) {
        return {
            responseError: function (response) {
                //console.log('HTTPInterceptor: Failed Response!');
                $rootScope.$broadcast({
                    401: AUTH_EVENTS.notAuthenticated,
                    403: AUTH_EVENTS.notAuthorized,
                    419: AUTH_EVENTS.sessionTimeout,
                    440: AUTH_EVENTS.sessionTimeout,
                    500: AUTH_EVENTS.serverError
                }[response.status], response);
                return $q.reject(response);
            },
            // automatically attach Authorization header
            request: function(config) {
                //console.log('AuthInterceptor request for -->',config.url);
                var feedbackToken = AuthService.getFeedbackToken();
                var token = AuthService.getToken();
                if(config.url.indexOf('/api/') === 0
                        || config.url.indexOf('/core/') === 0
                    ) {
                    if(token){
                        config.headers.Authorization = 'JWT ' + token;
                    }
                    else if(feedbackToken){
                          config.headers.Authorization = 'Bumper '+feedbackToken;

                    }
                    config.headers.source = AuthService.source;
                }

                return config;
            },

            // If a token was sent back, save it
            response: function(res) {
                //console.log('AuthInterceptor response', res.headers());
                if(res.config.url.indexOf('/api/') === 0 && res.data.token) {
                    AuthService.saveToken(res.data.token);
                }

                return res;
            }
        };
    })
    .factory('AuthResolver', function ($http, AuthService, UserService) {
        return {
            resolve: function () {
                AuthService.setSource();
                var jwt_token = AuthService.getToken();
                if(jwt_token){
                    //console.log('JWT token parsed->',AuthService.parseJwt(jwt_token));
                    var get_user_id = AuthService.parseJwt(jwt_token).user_id;
                    return $http.get('/api/user/'+get_user_id+'/get_user_profile_with_token/').success(function(data){
                        //console.log('Getting user data-->', data);
                        UserService.setCurrentUser(data.user);
                    });
                }
            }
        };
    })
;