angular.module('ops.views.base', [
    'ops.services.auth',
    'ops.services.common',
    'ops.services.user'
])
    .controller('BaseCtrl', function BaseCtrl($rootScope,$window,$scope,$state, $stateParams, UserService, AUTH_EVENTS,
                                              CommonService, BookingService, DataService, BOOKING_EVENTS) {
        var self = this;
        self.showFollowupButtomButton = false;
        self.topSearchBookingId = null;
        self.baseFilters = {cities:[]};
        self.currentUser  = UserService.getCurrentUser();
        var dataInFollowUp = DataService.getFollowupDataFromLocal();
        if (dataInFollowUp){
            self.showFollowupButtomButton = true;
            self.openFolloupPopup = true;
            updateFollowUpData();
        }
        else {
            self.showFollowupButtomButton = false;
            self.openFolloupPopup = false;
        }
        CommonService.getCities().then(function(res){
            self.cities = res;
        });
        CommonService.getMasterData().then(function(res){
            self.followupResults = res.followup_results;
        });
        var storageHandler = function (data) {
            //data.key == notes
            if(data.key == 'FollowUpData'){

                if(data.newValue != data.oldValue){
                    updateNotes();

                }

            }
            //data.newValue!= data.oldValue


        };
        window.addEventListener("storage", storageHandler, false);

        function getSelectedCities() {
            var cities = CommonService.getSelectedCities();
            var cities_dicts = [];
            for(var i=0; i<cities.length; i++){
                cities_dicts.push({'id': cities[i]});
            }
            self.baseFilters = {
                cities: cities_dicts
            };
        }
        getSelectedCities();

        function baseFiltersChanged(){
            var cities = [];
            if(self.baseFilters.cities.length === 0){
                self.baseFilters.cities = [{'id':1}];
            }

            for(var i=0; i<self.baseFilters.cities.length; i++){
                cities.push(self.baseFilters.cities[i].id);
            }

            CommonService.setSelectedCities(cities);
            $scope.$broadcast('baseFilterCitiesChanged', '');
        }

        function goToBooking(){
            if(self.topSearchBookingId){
                $state.go('base.bookings.editBooking.summary',{bookingId: self.topSearchBookingId});
                self.topSearchBookingId = null;
            }
        }

        function logout(){
            var response = UserService.logout();
            response.success(function(){
                $rootScope.$broadcast(AUTH_EVENTS.logoutSuccess, {});
            });
        }

        function getActiveAlerts(){
            CommonService.getActiveAlerts()
                .then(function (data) {
                    if (data) {
                        self.activeAlerts = data;
                    }
                });
        }
        function updateNotes() {
            var followUpData = DataService.getFollowupDataFromLocal();
            if(followUpData){
                self.modalItem.notes=followUpData.notes;
            }
            else {
                self.showFollowupButtomButton = false;
                self.openFolloupPopup = false;
            }

        }
        function updateFollowUpData() {
            self.openFolloupPopup = true;
            self.showFollowupButtomButton = true;
            self.errorMsgs =[];
            self.modalItem = {
                "notes": ""
            };
            var data = DataService.getFollowupDataFromLocal();
            self.followUpId = data.id;
            jQuery(".form_datetime").datetimepicker({
                format: "yyyy-mm-dd hh:ii",
                autoclose: true,
                todayBtn: true,
                startDate: "2015-07-01 10:00",
                minuteStep: 10,
                orientation: 'auto',
                pickerPosition: 'top-left'
                //minView: 1
            });
            updateNotes();
        }
        //to be called by Click to call
        function addCallNotes(mode, id){
            //mode 1 - booking 2- inquiry
            DataService.saveFollowupData(mode, id);
            updateFollowUpData();
        }
        function saveText() {
            DataService.saveNotesToLocal(self.modalItem.notes);
        }
        function submitFollowup() {
            var followUpData = DataService.getFollowupDataFromLocal();
            var data = {
                'followup': [{
                    "note": "Click To Call: " + followUpData.notes,
                    "result": self.modalItem.result && self.modalItem.result.id != '?' ? self.modalItem.result.id: null,
                    "comm_mode": "1"
                }]
            };
            if(self.modalItem.result.action_type == 1 && moment(self.modalItem.nextFollowUpDt) < moment.now()){
                self.errorMsgs.push("Next Followup date should be greater than now.");
                return false;
            }
            if(self.modalItem.result.action_type == 1 && self.modalItem.nextFollowUpDt){
                if(followUpData.mode === 1) {
                    data.next_followup = self.modalItem.nextFollowUpDt;
                }
                if(followUpData.mode === 2){
                    data.followup[0].next_followup_dt =self.modalItem.nextFollowUpDt;
                }
            }
            if(followUpData.mode === 1) {
                BookingService.saveBookingFollowups(followUpData.id, data)
                    .success(function (response) {
                        sweetAlert("success", "Followup Saved", "success");
                        DataService.clearNotesFromLocal();
                        self.openFolloupPopup = false;
                        self.showFollowupButtomButton = false;
                        //close chat popup
                        $rootScope.$broadcast(BOOKING_EVENTS.LoadFollowupBooking,{});
                    })
                    .error(function (response) {
                        var status = response.status;
                        if (status == '401') {
                            sweetAlert("Error", "You don't have permission required to do this action.", "error");
                        } else if (status == '400') {
                            self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                        } else {
                            sweetAlert("Error", "Errors: Server Error", "error");
                        }
                    });
            }else {
                UserService.saveUserInquiryFollowups(followUpData.id, data)
                    .success(function(response){
                        sweetAlert("success", "Followup Saved", "success");
                        DataService.clearNotesFromLocal();
                        self.openFolloupPopup = false;
                        self.showFollowupButtomButton = false;
                        $rootScope.$broadcast(BOOKING_EVENTS.LoadFollowupInquiry,{});
                    })
                    .error(function(response){
                        var status = response.status;
                        if(status == '401'){
                            sweetAlert("Error", "You don't have permission required to do this action.", "error");
                        }else if(status == '400'){
                            self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                        }else{
                            sweetAlert("Error", "Errors: Server Error", "error");
                        }
                    });
            }
        }
// listen for the event in the relevant $scope
        $scope.$on('alertsUpdated', function (event, data) {
            getActiveAlerts();
        });
        getActiveAlerts();

        self.logout = logout;
        self.goToBooking = goToBooking;
        self.baseFiltersChanged = baseFiltersChanged;
        self.addCallNotes = addCallNotes;
        self.submitFollowup = submitFollowup;
        self.saveText = saveText;
        self.updateFollowUpData =updateFollowUpData;
        self.updateNotes = updateNotes;
    })
;
