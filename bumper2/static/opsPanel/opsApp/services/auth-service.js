
angular.module('ops.services.auth',[
])
    .service('AuthService', function($window, $location){
        var self = this;
        self.source = 'opsPanel';

        self.getJWTTokenName = function(){
            return $location.host()+'jwtToken';
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
            //console.log('Token Name->', self.getJWTTokenName());
            return $window.localStorage[self.getJWTTokenName()];
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
    })
    .factory('AuthInterceptor', function ($rootScope, $q, AUTH_EVENTS, AuthService, GlobalDataService) {
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
                var token = AuthService.getToken();
                if((config.url.indexOf('/api/') === 0 || config.url.indexOf('/core/') === 0) && token) {
                    config.headers.Authorization = 'JWT ' + token;
                }
                config.headers.source = AuthService.source;
                if(config.url.indexOf('/static/') === 0 && config.url.indexOf('html') != -1){
                    config.url = config.url + '?v=' + GlobalDataService.getStaticFileVersion();
                }
                return config;
            },

            // If a token was sent back, save it
            response: function(res) {
                //console.log('AuthInterceptor response');
                if(res.config.url.indexOf('/get_user_profile_with_token/') >= 0 && res.data.token) {
                    AuthService.saveToken(res.data.token);
                }

                return res;
            }
        };
    })
    .factory('AuthResolver', function ($http, AuthService, UserService) {
        return {
            resolve: function (user_id) {
                return $http.get('/api/user/'+user_id+'/get_user_profile_with_token/').success(function(data){
                    //console.log('Inside success of Auth Resolver.',data);
                    //AuthService.saveToken(data.token);
                    UserService.setCurrentUser(data.user, data.permissions);
                });
            }
        };
    })
;