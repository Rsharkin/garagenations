
angular.module('ops.services.common',[
])
    .service('CommonService', function($http, $window){
        var self = this,
            URLS={
                FETCH_REPORT_DATA: '/api/report/build_report/',
                FETCH_RECORDINGS: '/api/report/get_recordings/',
                FETCH_WORKSHOP_SCHEDULE: '/api/report/get_workshop_schedule/',
                FETCH_RECORDINGS_WITHIN_DATES: '/api/report/get_recordings_within_dates/',
                FETCH_ADS_DATA: '/api/report/get_ads_data/',
                FETCH_MATER_DATA: '/api/master-data/',
                FETCH_USER_CAR: '/api/usercar/',
                NOTIFY_USER: '/api/notify-users/send_notification/',
                NOTIFY__REQUEST_USER_LOCATION: '/api/notify-users/request_location/',
                UPDATE_ENTITY_CHANGE: '/api/entity-change/',
                UPDATE_WORKSHOP_ALERT_ENDPOINT: '/api/raise-alert/',
                GET_COGNITO_TOKEN: '/api/get-cognito-token/',
                SCRATCH_FINDER_ENDPOINT: '/api/sflead/',
                CITY_ENDPOINT: '/api/city/',
                CREDIT_HISTORY:'/api/credit-history/'
            };

        self.setSelectedCities = function(cities){
            //console.log('Cities to be saved in local', cities);
            if(cities.length>0){
                $window.localStorage.baseFiltersCities = cities;
            }
        };

        self.getSelectedCities = function(){
            var cities = $window.localStorage.baseFiltersCities;
            //console.log('Cities in local->', cities);
            if(!cities){
                // settings bangalore as default city.
                cities = '1';
            }
            //console.log('Cities to be retrived from local', cities);
            return cities.split(',');
        };

        self.getActiveAlerts = function(){
            return $http.get(URLS.UPDATE_WORKSHOP_ALERT_ENDPOINT+'?resolved=false').then(function(response){
                return response.data.results;
            });
        };

        self.getAllAlerts = function(){
            return $http.get(URLS.UPDATE_WORKSHOP_ALERT_ENDPOINT).then(function(response){
                return response.data.results;
            });
        };

        self.markAlertResolved = function(alertId){
            return $http.patch(URLS.UPDATE_WORKSHOP_ALERT_ENDPOINT+alertId+"/", {resolved:true}).then(function(response){
                return response;
            });
        };

        self.raiseAlert = function(data){
            return $http.post(URLS.UPDATE_WORKSHOP_ALERT_ENDPOINT, data).then(function(response){
                return response;
            });
        };

        self.getAdsData = function(){
            return $http.get(URLS.FETCH_ADS_DATA).then(function(response){
                return response.data.data;
            });
        };

        self.getReportData = function(report_type, filters, groupOp){
            var _search = false;
            groupOp = groupOp ? groupOp: 'AND';

            var _filters = {'groupOp': groupOp,'rules':[]};
            if(filters && filters.length>0){
                _search = true;
                for(var i=0; i< filters.length;i++){
                    _filters.rules.push(filters[i]);
                }
            }
            return $http.get(URLS.FETCH_REPORT_DATA+'?report_type='+report_type+'&_search='+_search+'&filters='+JSON.stringify(_filters)).then(function(response){
                return response.data.data;
            });
        };

        self.getWorkshopSchedule = function(inputs){
            var q_str = '?resources='+JSON.stringify(inputs.resources);
                q_str += "&removeList="+inputs.removeList;
                q_str += "&useCurrentStatus="+inputs.useCurrentStatus;
                q_str += "&workshop="+inputs.workshop;

            return $http.get(URLS.FETCH_WORKSHOP_SCHEDULE + q_str).then(function(response){
                return response.data.data;
            });
        };

        self.getRecordings = function(phoneNumbersCSV, startTime, endTime){
            var url = startTime && endTime ? URLS.FETCH_RECORDINGS_WITHIN_DATES : URLS.FETCH_RECORDINGS;
            return $http.get(url + "?phone_numbers="+ phoneNumbersCSV+"&start_date="+startTime+"&end_date="+endTime).then(function(response){
                return response.data.recordings;
            });
        };

        self.getMasterData = function(bookingCity){
            var extraArgs= '';
            if(bookingCity){
                if(extraArgs === ''){
                    extraArgs = '?city_id=' + bookingCity;
                }else{
                    extraArgs = '&city_id=' + bookingCity;
                }
            }
            return $http.get(URLS.FETCH_MATER_DATA+extraArgs).then(function(response){
                return response.data;
            });
        };

        self.getCities = function(){
            return $http.get(URLS.CITY_ENDPOINT).then(function(response){
                return response.data.results;
            });
        };

        self.getUserCar = function(userCarId){
            return $http.get(URLS.FETCH_USER_CAR + userCarId + "/").then(function(result){
                return result.data;
            });
        };

        self.getUserCarsByUserId = function(userID){
            return $http.get(URLS.FETCH_USER_CAR+"?user="+userID).then(function(result){
                return result.data;
            });
        };

        self.saveUserCar = function(userCarId, data){
            return $http.patch(URLS.FETCH_USER_CAR + userCarId + "/", data);
        };

        self.notifyUser = function(noticeDetails){
            return $http.post(URLS.NOTIFY_USER,noticeDetails);
        };

        self.requestUserLocation = function(noticeDetails){
            return $http.post(URLS.NOTIFY__REQUEST_USER_LOCATION, noticeDetails);
        };

        self.updateEntityChange = function(data){
            return $http.post(URLS.UPDATE_ENTITY_CHANGE, data);
        };

        self.getEntityChanges = function(contentId){
            return $http.get(URLS.UPDATE_ENTITY_CHANGE+"?content_id="+contentId).then(function(response){
                return response.data.results;
            });
        };

        self.getCognitoToken = function(){
            return $http.get(URLS.GET_COGNITO_TOKEN);
        };

        self.updateScratchFinderLead = function(leadId, data){
            return $http.patch(URLS.SCRATCH_FINDER_ENDPOINT+leadId+"/", data);
        };

        self.getScratchFinderLeadsByReferrer = function (referrerUserId){
            var query_string = '';
            if(referrerUserId){
                query_string += "?user=" + referrerUserId;
            }
            return $http.get(URLS.SCRATCH_FINDER_ENDPOINT+query_string).then(function(response){
                return response.data.results;
            });
        };
        self.getUserCredits= function (userID) {
            return $http.get(URLS.CREDIT_HISTORY+"?user="+userID).then(function(result){
                return result.data;
            });
        };
    })
;