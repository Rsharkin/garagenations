/**
 * Created by rishisharma on 06/06/16.
 */
angular.module('ops.views.createUsers', [
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data'
]).controller('CreateUserController', function CreateUserController($state,$scope, $stateParams,DataService,
                                                                    UserService, CommonService){
    var self=this;
    self.allowCreateUser = false;
    self.flow = $stateParams.flow? $stateParams.flow: 'booking';

    CommonService.getMasterData().then(function(res){
        self.userSources = res.new_sources;
    });
    CommonService.getCities().then(function(res){
        self.cities = res;
    });

    self.newUser= {
        "name":null,
        "email":null,
        "phone":null,
        "source": null,
        "city": null
    };
    self.message=null;

    DataService.newBooking={};

    function userCreationSuccess(result){
        sweetAlert("User exists", "proceeding with existing user");
        if(self.flow === 'inquiry') {
            $state.go('base.userInquiry.CreateUserInquiry', {'userId' : result.user.id });
        }else{
            $state.go('base.createUser.addUserCar');
        }
    }
    function userSelection(){
        DataService.newBooking.userSource = self.userDetails.source;
        DataService.newBooking.userCity = self.userDetails.city.id;
        DataService.newBooking.userId = self.userDetails.id;
        if(self.flow === 'inquiry') {
            $state.go('base.userInquiry.CreateUserInquiry', {'userId' : self.userDetails.id });
        }else{
            $state.go('base.createUser.addUserCar');
        }
    }
    function submitForm(userFrom) {
        if (userFrom.$valid) {
            self.valid=true;
            //console.log('source while creating user.',self.newUser.source);
            DataService.newBooking.userSource = self.newUser.source;
            DataService.newBooking.userCity = self.newUser.city;
            self.newUser.city_id = self.newUser.city;

            var res = UserService.createUser(self.newUser);
            res.success(function (result) {
                DataService.newBooking.userId = result.user.id;
                sweetAlert("user created");
                if(self.flow === 'inquiry'){
                    $state.go('base.userInquiry.CreateUserInquiry', {'userId' : result.user.id });
                }else{
                    $state.go('base.createUser.addUserCar');
                }

            }).error(function (result, status) {
                    if (status == 409) {
                        DataService.newBooking.userId = result.user.id;
                        var to_update = false;
                        var data = {};
                        if(self.newUser.email && result.user.email != self.newUser.email){
                            to_update = true;
                            data.email= self.newUser.email;
                        }
                        if(self.newUser.name && result.user.name != self.newUser.name){
                            to_update = true;
                            data.name= self.newUser.name;
                        }
                        if(to_update){
                            UserService.updateUserById(result.user.id,data).then(function(){
                                userCreationSuccess(result);
                            });
                        }else{
                            userCreationSuccess(result);
                        }
                    }
                    else {
                        sweetAlert("error creating user, contact admin");
                    }
                }
            );
        }
        else {
            self.valid=false;
        }
    }
    function searchUser(){
        UserService.getUserByPhone(self.searchUserPhone).then(function(userDetails){
            self.userDetails = userDetails;
            self.allowCreateUser = true;
            //console.log('userdetails', self.userDetails);
            if(self.userDetails){
                self.newUser= {
                    "name":self.userDetails.name,
                    "email":self.userDetails.email,
                    "phone": self.searchUserPhone,
                    "source": self.userDetails.source,
                    "city": ""+self.userDetails.city.id
                };
            }else{
                self.newUser= {
                    "name":null,
                    "email":null,
                    "phone":null,
                    "source": null,
                    "city": null
                };
            }
        });
    }

    self.submitForm=submitForm;
    self.searchUser=searchUser;
    self.userSelection=userSelection;
});
