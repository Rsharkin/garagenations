/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingDocuments',[
    'ops.services.booking',
    'ngFileUpload'

]).controller('EditBookingDocumentCtrl', function EditBookingDocumentCtrl($state,$uibModal, $scope, BookingService){
    var self = this;
    self.panelList = [];
    self.booking = BookingService.getCurrentBooking();

    BookingService.getPanelList().then(function (result) {
        if(result){
            self.panelList = result.data.results;
        }
    });

    function getUniqueGroups(array){
        var unique = {},
            distinct = [],
            dataGroupWise = [],
            data = [],
            hasItemsWithIssue = false,
            hasItemsWithMismatch = false;

        for( var i in array ){
            if( typeof(unique[array[i].group_num]) == "undefined"){
                distinct.push(array[i].group_num);
            }
            unique[array[i].group_num] = 0;
        }

        for( var j in distinct ){
            data = _.filter(array,{'group_num':distinct[j]});
            hasItemsWithIssue = _.some(data,
                function(o){if(o.is_applicable && o.has_issue){return true;} });

            hasItemsWithMismatch = _.some(data,
                function(o){if(o.mismatch){return true;} });

            dataGroupWise.push({
                group_num: distinct[j],
                created_at: data[0].created_at,
                updated_by_name: data[0].updated_by_details.name,
                updated_by_num: data[0].updated_by_details.ops_phone,
                hasItemsWithIssue:hasItemsWithIssue,
                hasItemsWithMismatch:hasItemsWithMismatch,
                data: data
            });
        }
        return dataGroupWise;
    }

    BookingService.getBookingChecklist(self.booking.id, 8).then(function(res){
        self.InteriorPhotosGroupWise = res;
    });

    BookingService.getBookingChecklist(self.booking.id, 1).then(function(res){
        self.electricalGroupWise = getUniqueGroups(res);
    });

    BookingService.getBookingChecklist(self.booking.id, 2).then(function(res){
        self.inventoryGroupWise = getUniqueGroups(res);
        console.log('inventoryGroupWise',self.inventoryGroupWise);
    });

    function showChecklistItems(items, typeOfChecklist){
        $uibModal.open({
            templateUrl: typeOfChecklist === 'images'?'views/checklist-images.html': 'views/checklist-details.html',
            controller: ShowChecklistDetailsModalInstanceCtrl,
            controllerAs: 'checklistCtrl',
            resolve: {
                items: function () {
                    return items;
                },
                typeOfChecklist: function () {
                    return typeOfChecklist;
                }
            }
        });
    }
    function getDocuments(){
        BookingService.getJobCards(self.booking.id)
            .then(function (response) {
                self.jobCards = response.data.results;

                // for(var i=0;i<self.jobCards.length;i++){
                //     for(var j=0;j<self.panelList.length;j++){
                //         if(self.jobCards[i].panel==self.panelList[j].id){
                //             self.jobCards[i].name = self.panelList[j].name;
                //         }
                //     }
                // }
            });
    }

    function openModal(imageUrl) {
        $uibModal.open({
            templateUrl: 'views/openImageModal.html',
            controller: imageModalInstanceCtrl,
            controllerAs: 'imageModal',
            size:'lg',
            resolve: {
                imageUrl: function () {
                    return imageUrl;
                }
            }
        });
    }
    // self.openLightboxModal = function (url) {
    //     self.images = [
    //         {
    //             'url': url
    //         }];
    //     Lightbox.openModal(self.images,0);
    // };
    // listen for the event in the relevant $scope
    $scope.$on('bookingUpdated', function () {
        getDocuments();
    });

    getDocuments();
    self.openModal = openModal;
    self.showChecklistItems = showChecklistItems;
});
function imageModalInstanceCtrl(imageUrl){
    var self = this;
    self.imageUrl = imageUrl;
}