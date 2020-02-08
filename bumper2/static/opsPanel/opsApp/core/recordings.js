angular.module('ops.views.recordings',[
    'ops.services.common'
])
    .controller('RecordingsCtrl', function RecordingsCtrl(CommonService, $stateParams){
        var self = this;
        self.ajax_loading = false;
        self.phoneNumbers = $stateParams.phoneNumbers? $stateParams.phoneNumbers + ',91'+$stateParams.phoneNumbers: '';
        self.recordings = [];

        function fetchRecordings(start_date, end_date){
            self.ajax_loading = true;
            CommonService.getRecordings(self.phoneNumbers, start_date, end_date).then(function(res){
                if(res && res.length>0){
                    self.ajax_loading = false;
                    self.recordings = res[0];
                    for(var i=0; i<self.recordings.length; i++){
                        var recording_path = self.recordings[i].final_recording_url.replace('+', '%2B');
                        self.recordings[i].full_path = 'https://telephony.ninjacrm.com/api/cdr/fetchRecordingFile.php?dealer=bumper&action=getFile&file=' + recording_path;
                    }
                }else{
                    self.ajax_loading = false;
                    sweetAlert("No Recordings", "If entering manually, please make sure phone numbers are entered properly without spaces", "warning");
                }
            });
        }
        if(self.phoneNumbers){
            fetchRecordings();
        }
        self.date_range_options = {
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            eventHandlers: {'apply.daterangepicker': function(ev, picker) {
                fetchRecordings(picker.startDate.format('YYYY-MM-DD'), picker.endDate.format('YYYY-MM-DD'));
            }}
        };
        self.fetchRecordings = fetchRecordings;
    })
;
