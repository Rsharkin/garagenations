
angular.module('ops.services.user',[
])
    .service('UserService', function($http, $window, AuthService){
        var self = this,
            current_user = null;

        self.dontShowCustomerNum = true;

        URLS={
            USER_LOGOUT: '/core/logout/',
            USER_ENDPOINT: '/api/user/',
            USER_ADDRESS_ENDPOINT: '/api/user-address/',
            CREATE_USER:"/api/user/create-user/",
            USER_INQUIRY_ENDPOINT:"/api/user-inquiry/",
            DRIVER_LOCATION_ENDPOINT:"/api/driver-location/"
        };

        self.userId= null;

        self.getCustomerNumber = function(phoneNumber){
            if(phoneNumber){
                var perm_see_cust_num = self.doesUserHasPermission('core.see_customer_number');
                //console.log('perm_see_cust_num->', perm_see_cust_num);
                if(self.dontShowCustomerNum && !perm_see_cust_num){
                    return "XXXXXX" + phoneNumber.substr(-4);
                }
            }
            return phoneNumber;
        };

        self.setCurrentUser = function(user_obj, permissions){
            if(user_obj){
                current_user = user_obj;
            }
            if(permissions){
                current_user.permissions = permissions;
            }
        };

        self.getCurrentUser = function(){
            return current_user;
        };

        self.doesUserHasPermission = function(permission){
            return current_user.permissions.indexOf(permission) !== -1;
        };

        self.isUserOnlyInOneGroup = function(groupName){
            var userGroups = [];

            for(var i=0;i<current_user.groups.length;i++){
                if(current_user.groups[i].name !== 'OpsUser'){
                    userGroups.push(current_user.groups[i].name);
                }
            }
            return (userGroups.length ===1 && userGroups.indexOf(groupName) >= 0);
        };

        self.isUserInGroup = function(groupNames){
            var userGroups = [];

            for(var i=0;i<current_user.groups.length;i++){
                userGroups.push(current_user.groups[i].name);
            }
            var allow_only_workshop_scheduler = false;

            if(groupNames.length === 1 && groupNames[0] === "WorkshopScheduler"){
                allow_only_workshop_scheduler = true;
            }
            if(userGroups.indexOf('OpsAdmin') >= 0 && !allow_only_workshop_scheduler){
                return true;
            }
            //console.log(userGroups);
            var found = false;
            angular.forEach(groupNames, function(groupName, index){
                //console.log('matching grp ',groupName,userGroups.indexOf(groupName));
                if (userGroups.indexOf(groupName) >= 0){
                    //console.log('found match');
                    found = true;
                    return true;
                }
            });
            return found;
        };

        self.getUserById = function(userId){
            return $http.get(URLS.USER_ENDPOINT + userId + "/").then(function(response){
                return response.data;
            });
        };

        self.getUserByPhone = function(phone){
            return $http.get(URLS.USER_ENDPOINT+ "?phone="+phone).then(function(response){
                return response.data.results?response.data.results[0]:null;
            });
        };

        self.updateUserById = function(userId, data){
            return $http.patch(URLS.USER_ENDPOINT + userId + "/", data).then(function(response){
                return response.data;
            });
        };

        self.getOpsAgents= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=OpsUser&ordering=name&is_active=true").then(function(response){
                // console.log('list of ops users', response);
                return response.data.results;
            });
        };

        self.getDrivers= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=Driver&ordering=name").then(function(result){
                return result.data.results;
            });
        };

        self.getDriverLocation= function(){
            return $http.get(URLS.DRIVER_LOCATION_ENDPOINT).then(function(result){
                return result.data.results;
            });
        };

        self.getActiveDrivers= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=Driver&is_active=true&ordering=name").then(function(result){
                return result.data.results;
            });
        };

        self.getUsersByRole= function(role){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=" + role).then(function(result){
                return result.data.results;
            });
        };

        self.getWorkshopManagers= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=WorkshopManager").then(function(result){
                return result.data.results;
            });
        };
        self.getWorkshopExecutives= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=WorkshopExecutive").then(function(result){
                return result.data.results;
            });
        };
        self.getWorkshopAssistantManager= function(){
            return $http.get(URLS.USER_ENDPOINT + "?group_name=WorkshopAssistantManager").then(function(result){
                return result.data.results;
            });
        };

        self.getUserAddressByUserId = function(userId){
            return $http.get(URLS.USER_ADDRESS_ENDPOINT+"?user=" + userId).then(function(response){
                return response.data;
            });
        };

        self.saveUserAddress = function(userAddress){
            if(userAddress.id){
                return $http.patch(URLS.USER_ADDRESS_ENDPOINT + userAddress.id + '/', userAddress);
            }else{
                return $http.post(URLS.USER_ADDRESS_ENDPOINT, userAddress);
            }
        };

        self.logout = function() {
            $window.localStorage.removeItem(AuthService.getJWTTokenName());
            return $http.post(URLS.USER_LOGOUT, {
                redirect_field_name: '/core/login/'
            });
        };
        self.createUser =function (user) {
            return $http.post(URLS.CREATE_USER,user);
        };

        self.getUserInquiryById = function(userInquiryId){
            return $http.get(URLS.USER_INQUIRY_ENDPOINT + userInquiryId + "/").then(function(result){
                return result.data;
            });
        };

        self.getUserInquiryByUserId = function(userId){
            return $http.get(URLS.USER_INQUIRY_ENDPOINT + "?user="+ userId).then(function(result){
                return result.data.results;
            });
        };

        self.updateUserInquiry = function(userInquiryId, data){
            return $http.patch(URLS.USER_INQUIRY_ENDPOINT + userInquiryId + "/", data).then(function(result){
                return result.data;
            });
        };
        self.createUserInquiry = function(data){
            return $http.post(URLS.USER_INQUIRY_ENDPOINT, data).then(function(result){
                return result.data;
            });
        };

        self.getUserInquiryFollowups = function(userInquiryId){
            return $http.get(URLS.USER_INQUIRY_ENDPOINT + userInquiryId + "/followup/").then(function(result){
                if(result.data) return result.data.followup;
            });
        };

        self.saveUserInquiryFollowups = function(userInquiryId, followupData){
            return $http.patch(URLS.USER_INQUIRY_ENDPOINT + userInquiryId + "/followup/", followupData);
        };

    })
;