/**
 * Created by rishisharma on 20/10/16.
 */
angular.module('bumper.view.contact', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('ContactController', function ContactController($anchorScroll,$location,$timeout,$scope,BUMPER_EVENTS, CommonService, $mdToast,BookingDataService, UserService, CommonModel) {
        var self = this;
        self.isOpen = false;
        $("img.lazy").lazyload();
        var city = BookingDataService.getSelectedCityFromLocal();
        self.userDetails ={
            "name":'',
            "email":'',
            "mobile":''
        };
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);


        self.isDeviceMobile = false;
        Tawk_API = Tawk_API || {};
        self.isDeviceMobile = CommonService.mobileBrowser();
        if(self.isDeviceMobile ){
            try{
                Tawk_API.showWidget();
            }
            catch (e){
                //tawk api not laded
            }
        }
        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            userInquiry();
        });
        function userInquiry(action) {
            self.comment=action;
            self.userMessage={
                "inquiry":null,
                "city":city.id
            };
            self.userExist=self.userExist = UserService.getCurrentUser();
            if (self.userExist){
                // post enquiry....
                if(self.comment==1){
                    self.userMessage.inquiry="Request for call back";
                }
                else{
                    self.userMessage.inquiry=self.comment;
                }
                var res= CommonModel.sendUserInquiry(self.userMessage);
                res.success(function (result) {
                    self.comments=null;
                    //Show-confirmation
                    self.showSimpleToast = function() {
                        $mdToast.show(
                            $mdToast.simple()
                                .textContent('Thank you! we will call you shortly')
                                .hideDelay(1000)
                                .theme('default')
                        );
                        self.showHelp=false;
                    };
                    self.showSimpleToast();
                }).error( function (result) {
                    self.error=result.inquiry[0];
                })
            }
            else{
                self.signupForComments=true;
                //ask for login ....
                if(self.comment==1){
                    $scope.base.showUserPopup(false, 'Panel Page Request for call back click');
                }else{
                    $scope.base.showUserPopup(false, 'Panel Page comments button click');
                }

            }
        }
        self.userInquiry=userInquiry;
    });
