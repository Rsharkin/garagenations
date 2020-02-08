
angular.module('ops.services.data',[
])
    .service('DataService', function($window){
        var self = this;
        self.dataForFollowUp = {
            mode:null,
            id:null,
            notes:""
        };
        self.userCar=null;
        self.masterData = null; // not using this as full time cache, as we do not currently have a proper way to
        // invalidate the cache. So this data is refereshed at some places where not doing it could save performance.
        self.newBooking={};
        function saveNotesToLocal(note) {
            var dict = getFollowupDataFromLocal();
            dict.notes = note;
            $window.localStorage.FollowUpData = JSON.stringify(dict);
        }
        function saveFollowupData(mode,id) {
            self.dataForFollowUp.mode = mode;
            self.dataForFollowUp.id = id;
            $window.localStorage.FollowUpData = JSON.stringify(self.dataForFollowUp);
        }
        function getFollowupDataFromLocal() {
            var data = $window.localStorage.FollowUpData;
            if(data){
                data = JSON.parse(data);
                return data;
            }
            else {
                return null;
            }
        }
        function clearNotesFromLocal() {
            $window.localStorage.FollowUpData = JSON.stringify(null);
        }

        function saveRemovedBookings(comma_sep_ids){
            $window.localStorage.removeList = comma_sep_ids;
        }
        function getRemovedBookings(){
            return $window.localStorage.removeList;
        }
        function clearRemovedBookings(){
            $window.localStorage.removeList = null;
        }
        self.getFollowupDataFromLocal = getFollowupDataFromLocal;
        self.saveNotesToLocal = saveNotesToLocal;
        self.clearNotesFromLocal = clearNotesFromLocal;
        self.saveFollowupData = saveFollowupData;
        self.saveRemovedBookings = saveRemovedBookings;
        self.getRemovedBookings = getRemovedBookings;
        self.clearRemovedBookings = clearRemovedBookings;
    })
;