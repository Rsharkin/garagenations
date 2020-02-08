/**
 * Created by Indy on 22/05/17.
 */
angular.module('ops.views.createUserInquiry',[
    'ops.services.common',
    'ops.services.user',
    'ops.services.booking',
    'ops.services.data'
]).controller('CreateUserInquiryCtrl', function(CommonService, UserService, BookingService, $stateParams, $state,
                                                  DataService){
        var self = this;
        self.editedInquiry = {
            'user_id': $stateParams.userId,
            'source': DataService.newBooking.userSource,
            'city': DataService.newBooking.userCity
        };
        self.selectedCar = null;
        self.selectedCarId = null;
        self.followups = null;
        self.userId = $stateParams.userId;
        self.newFollowup = {};

        function getModel(searchText) {
            if(searchText) {
                self.selectedCar=null;
                BookingService.getModel( searchText )
                    .then( function (data) {
                        if (data.data.results) {
                            self.models = data.data.results;
                        }
                    });
            }
        }
        UserService.getOpsAgents().then(function(res){
            self.opsAgents = res;
        });
        function setSelectedCar(selected_car) {
            self.selectedCarId=selected_car.id;
            self.selectedCar=selected_car.id;
            if(selected_car) {
                jQuery('#search_car_text').val(selected_car.name);
            }
        }

        CommonService.getMasterData(DataService.newBooking.userCity).then(function(res){
            self.userSources = res.new_sources;
            self.inquiryStatuses = res.user_inquiry_statuses;
        });

        CommonService.getCities().then(function(res){
            self.cities = res;
        });

        function loadData(){
            UserService.getUserById(self.userId)
                .then(function (data) {
                    self.user = data;
                });
        }

        loadData();

        function createUserInquiry(){
            if(self.selectedCarId){
                self.editedInquiry.car_model_id = self.selectedCarId;
            }
            self.editedInquiry.lead_quality = self.editedInquiry.lead_quality ? parseInt(self.editedInquiry.lead_quality) : null;

            UserService.createUserInquiry(self.editedInquiry)
                .then(function (data) {
                    self.ajax_loading = false;
                    sweetAlert("success", "Inquiry Created", "success");
                    $state.go('base.userInquiry');
                });
        }

        self.setSelectedCar = setSelectedCar;
        self.getModel = getModel;
        self.createUserInquiry = createUserInquiry;
        self.createUserInquiry = createUserInquiry;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });
    })
;