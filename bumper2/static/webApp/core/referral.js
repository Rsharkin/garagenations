/**
 * Created by rishisharma on 21/11/16.
 */
angular.module('bumper.view.referral', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('ReferralController', function ReferralController(BUMPER_EVENTS, UserService, $scope, CommonModel) {
        var self =this;
        $("img.lazy").lazyload();
        self.currentUser  = UserService.getCurrentUser();
        $scope.$on(BUMPER_EVENTS.UserUpdated, function (event, data) {
            self.currentUser = UserService.getCurrentUser();
            loadReferralDetails();
        });
        function copy(element_id){
            // Create a "hidden" input
            var aux = document.createElement("input");
            // Assign it the value of the specified element
            aux.setAttribute("value", document.getElementById(element_id).innerHTML);
            // Append it to the body
            document.body.appendChild(aux);
            // Highlight its content
            aux.select();
            // Copy the highlighted text
            document.execCommand("copy");
            // Remove it from the body
            document.body.removeChild(aux);
        }
        function login() {
            $scope.base.showUserPopup(false, 'opening for referral');
        }

        function loadReferralDetails() {
            if(self.currentUser){
                var res = CommonModel.getReferralCode();
                res.success(function (result) {
                    if(result){
                        self.referralCode = result.results[0].code;
                        self.campaign = result.campaign;
                        var str = self.campaign.share_message;
                        self.campaign.share_message = str.replace("{%referral_code%}", self.referralCode);
                        str = self.campaign.share_title;
                        self.campaign.share_title = str.replace("{%referral_code%}", self.referralCode);
                        self.whatsAppText = encodeURIComponent(self.campaign.share_message);
                    }
                }).error(function () {
                    //console.log("error generating in referral code");
                });
            }
            else {
                //console.log("not logged in");
            }
        }
        loadReferralDetails();

        function facebookShare(){
            FB.ui({
                method: 'feed',
                mobile_iframe: true,
                link: 'http://bit.ly/BumperReferral',
                caption:self.campaign.description,
                description: self.campaign.share_message,
                name: self.campaign.share_title
            }, function(response){});
        }

        function twitterShare(){
            var url = "http://bit.ly/BumperReferral";
            var text = self.campaign.share_message;
            window.open('http://twitter.com/share?url='+encodeURIComponent(url)+'&text='+encodeURIComponent(text), '', 'left=0,top=0,width=550,height=450,personalbar=0,toolbar=0,scrollbars=0,resizable=0');
        }
        self.twitterShare = twitterShare;
        self.copy = copy;
        self.facebookShare = facebookShare;
        self.login = login;
    });