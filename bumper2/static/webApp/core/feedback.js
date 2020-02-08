/**
 * Created by rishisharma on 18/04/17.
 */
angular.module('bumper.view.feedback', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('FeedbackController', function FeedbackController($location, CommonModel, BookingDataService,AuthService) {
        var self = this;
        var data = {};
        $("tawkchat-minified-wrapper").css('display','none');

        $(".navbar").hide();
        //default rating
        self.rating1 = 1;
        self.rating2 = 1;
        self.rating3 = 1;
        $("img.lazy").lazyload();
        var queryParams = $location.search();
        self.token = queryParams.token;

        try{
            Tawk_API.hideWidget();
        }
        catch (e){
            //tawk api not laded
        }
        if(self.token){
            AuthService.saveFeedbackToken(self.token);
        }
        else {
            self.error = 'OOPS! Something Went Wrong';
        }
        self.loadRating = function() {
            console.log('rating',self.rating1);
            console.log('rating',self.rating2);
            console.log('rating',self.rating3);
            if (self.rating1 == 1) {
                $('#slider1 ._md-thumb').addClass('_md-thumb1').removeClass('_md-thumb3').removeClass('_md-thumb2');
            }
            if (self.rating1 == 2) {
                $('#slider1 ._md-thumb').addClass('_md-thumb2').removeClass('_md-thumb3').removeClass('_md-thumb1');
            }
            if (self.rating1 == 3) {
                $('#slider1 ._md-thumb').addClass('_md-thumb3').removeClass('_md-thumb1').removeClass('_md-thumb2');
            }
            if (self.rating2 == 1) {
                $('#slider2 ._md-thumb').addClass('_md-thumb1').removeClass('_md-thumb3').removeClass('_md-thumb2');
            }
            if (self.rating2 == 2) {
                $('#slider2 ._md-thumb').addClass('_md-thumb2').removeClass('_md-thumb3').removeClass('_md-thumb1');
            }
            if (self.rating2 == 3) {
                $('#slider2 ._md-thumb').addClass('_md-thumb3').removeClass('_md-thumb1').removeClass('_md-thumb2');
            }
            if (self.rating3 == 1) {
                $('#slider3 ._md-thumb').addClass('_md-thumb1').removeClass('_md-thumb3').removeClass('_md-thumb2');
            }
            if (self.rating3 == 2) {
                $('#slider3 ._md-thumb').addClass('_md-thumb2').removeClass('_md-thumb3').removeClass('_md-thumb1');
            }
            if (self.rating3 == 3) {
                $('#slider3 ._md-thumb').addClass('_md-thumb3').removeClass('_md-thumb1').removeClass('_md-thumb2');
            }
        };

        self.submit=function(){
            var res = CommonModel.getPaymentDetails(self.token);
            res.success(function (result) {
                //console.log("data",data);
                self.bookingData = result;
                data.booking = self.bookingData.id;
                data.experience_rating = self.rating1;
                data.value_for_money = self.rating2;
                data.work_quality = self.rating3;
                data.any_suggestions = self.suggestions;
                CommonModel.postFeedback(data).then(function(result){
                    if(result){
                        console.log("result",result);
                        //navigate somewhere
                        self.success = "Thank you for your feedback!"
                    }
                    else {
                        self.error = "Error in submitting feedback";
                    }
                });
            }).error(function () {
                self.error = "Error in getting booking details";
            });
        };

    });