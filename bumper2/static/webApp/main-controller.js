/**
 *
 * Main controller.js file
 * Other screens have there on controllers
 *
 *
 * Functions (controllers)
 *  - MainCtrl
 *
 *
 */
/**
 * MainCtrl - controller
 * Contains several global data used in different view
 *
 */
angular
    .module('bumper')
    .controller('MainCtrl', function MainCtrl($uibModal,$location, $state,CommonModel,BookingDataService) {
        var self = this;
        self.chatData ={};
        self.isDeviceMobile = false;
        var queryParams = $location.search();
        self.utm_source = queryParams.utm_source;
        self.utm_medium = queryParams.utm_medium;
        self.utm_campaign = queryParams.utm_campaign;
        var city = BookingDataService.getSelectedCityFromLocal();
        if( navigator.userAgent.match(/Android/i)
            || navigator.userAgent.match(/webOS/i)
            || navigator.userAgent.match(/iPhone/i)
            || navigator.userAgent.match(/iPad/i)
            || navigator.userAgent.match(/iPod/i)
            || navigator.userAgent.match(/BlackBerry/i)
            || navigator.userAgent.match(/Windows Phone/i)) {
            self.isDeviceMobile = true;
        }
        var  TawkAPI = Tawk_API||{};
        TawkAPI.onOfflineSubmit = function(data){
            if(data){
                self.chatData.name = data.name;
                self.chatData.email = data.email;
                self.chatData.city = city.id;
                self.chatData.phone = data.questions[2].answer;
                self.chatData.inquiry = data.questions[4].answer;
                self.chatData.source = 'chat';
                self.chatData.utm_source = self.utm_source;
                self.chatData.utm_medium = self.utm_medium;
                self.chatData.utm_campaign = self.utm_campaign;
                var res = CommonModel.createChatInquiry(self.chatData);
                res.success(function (result) {
                    //chat inquiry created
                }).error(function (result) {
                    //console.log("error",result);
                })
            }
        };
        // $(document).ready(function () {
        //     var modalInstance = $uibModal.open({
        //             templateUrl: 'views/common/ganesha-popup.html',
        //             controller: creativeController,
        //             controllerAs: 'creativeCtrl'
        //         }
        //     )
        // });

    });
function creativeController($uibModalInstance) {
    var self= this;
    self.close = function () {
        $uibModalInstance.close('');
    };
}
