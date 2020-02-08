/**
 * Created by rishisharma on 18/05/17.
 */
angular.module('bumper.view.checklist', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('ChecklistController', function ChecklistController (CommonModel,Lightbox,$location, AuthService, $scope, UserService, BUMPER_EVENTS) {
        var self=this;
        self.inventoryList =[];
        self.show1 = true;
        self.hideBlock= false;
        self.electricalList =[];
        self.jobCardImage = [];
        self.panelImage =[];
        self.interiorImage =[];
        $("img.lazy").lazyload();
        var queryParams = $location.search();
        $( document ).ready(function() {
            console.log( "ready!" );
            Tawk_API.hideWidget();
            
        });

        self.token = queryParams.token;
        if(self.token){
            AuthService.saveFeedbackToken(self.token);
        }
        self.statusId = queryParams.status_id;
        if(self.statusId == 3 ){
            self.hideBlock = false;
        }else {
            self.hideBlock = true;
        }
        self.openJobCardModal = function (index) {
            Lightbox.openModal(self.jobCardImage, index);
        };
        self.openInteriorModal = function (index) {
            Lightbox.openModal(self.interiorImage, index);
        };
        self.openPanelModal = function (index) {
            Lightbox.openModal(self.panelImage, index);
        };
        function loadChecklist() {
            var res = CommonModel.getPaymentDetails(self.token);
            res.success(function (result) {
                //console.log("data",data);
                self.bookingData = result;

                CommonModel.getPanelList().then(function (result) {
                    if(result){
                        self.panelList = result.data.results;
                    }
                });
                CommonModel.getBookingChecklist(self.bookingData.id, 2).then(function (result) {
                    if (result) {
                        self.inventoryList = result.data.results;
                    }
                });
                CommonModel.getBookingChecklist(self.bookingData.id, 1).then(function (result) {
                    self.electricalList = result.data.results;

                });
                CommonModel.getInteriorPhoto(self.bookingData.id, 8).then(function (result) {
                    self.carInteriorImage = result.data.results;
                    for(var i=0;i<self.carInteriorImage.length;i++){
                        self.interiorImage.push({'url': self.carInteriorImage[i].media[0].media_url, 'thumbUrl': self.carInteriorImage[i].media[0].media_url,'time':self.carInteriorImage[i].updated_at});
                    }

                    // console.log("interior image",self.interiorImage);
                });
                CommonModel.getJobCards(self.bookingData.id).then(function (result) {
                    self.jobCards = result.data.results;
                    for(var i=0;i<self.jobCards.length;i++){
                        if(self.jobCards[i].image_type ==1){
                            var dict= {'url': self.jobCards[i].media_url, 'thumbUrl': self.jobCards[i].media_url,'time':self.jobCards[i].updated_at};
                            self.jobCardImage.push(dict);
                        }
                        else if(self.jobCards[i].image_type ==3){
                            self.panelImage.push( {'url': self.jobCards[i].media_url, 'thumbUrl': self.jobCards[i].media_url,'name':self.jobCards[i].panel.name,'time':self.jobCards[i].updated_at});
                        }
                    }
                    // console.log("jobcar image",self.jobCardImage);
                    //console.log("panelImage",self.panelImage);

                });
            });
        }
        loadChecklist();
    });