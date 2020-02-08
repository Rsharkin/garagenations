angular.module('ops.views.reports', [
    'ops.services.common',
    'datatables'
])
    .controller('ReportBookingFollowupsCtrl', function ReportBookingFollowupsCtrl($state, $stateParams, CommonService,
                                                                                  $scope ) {
        var self = this;

        self.filters = {};
        self.dateRangeObj = null;
        self.cities = CommonService.getSelectedCities();
        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            apply_filters();
        });

        function getBookingFollowups(filters){
            CommonService.getReportData('report_booking_followups', filters)
                .then(function (data) {
                    if(data){
                        self.booking_followups_data = data.rows && data.rows.length?data.rows:[];
                        self.num_of_followups = self.booking_followups_data.length;
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }

        function apply_filters(){
            var dateRangeObj = self.dateRangeObj;
            var date_range = dateRangeObj? dateRangeObj: self.filters.date;
            var start_dt = '';
            var end_dt = '';

            if(date_range){
                start_dt = date_range.startDate.format('YYYY-MM-DD');
                end_dt = date_range.endDate.format('YYYY-MM-DD');
            }
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            if(start_dt && end_dt){
                filters.push({ 'op': 'deq', 'field': 'created_at', 'data': start_dt+'<=>'+end_dt });
            }else{
                filters.push({ 'op': 'deq', 'field': 'created_at', 'data': moment().format('YYYY-MM-DD')+'<=>'+moment().format('YYYY-MM-DD') });
            }
            getBookingFollowups(filters);
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
                self.dateRangeObj = picker;
                apply_filters();
            }}
        };


        // To load al records
        apply_filters();
        self.apply_filters = apply_filters;
    })
    .controller('ReportInquiryFollowupsCtrl', function ReportInquiryFollowupsCtrl($state, $stateParams, CommonService,
                                                                                  $scope ) {
        var self = this;

        self.filters = {};
        self.dateRangeObj = null;
        self.cities = CommonService.getSelectedCities();
        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            apply_filters();
        });

        function getFollowups(filters){
            CommonService.getReportData('report_inquiry_followups', filters)
                .then(function (data) {
                    if(data){
                        self.followups_data = data.rows && data.rows.length?data.rows:[];
                        self.num_of_followups = self.followups_data.length;
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }

        function apply_filters(){
            var dateRangeObj = self.dateRangeObj;
            var date_range = dateRangeObj? dateRangeObj: self.filters.date;
            var start_dt = '';
            var end_dt = '';

            if(date_range){
                start_dt = date_range.startDate.format('YYYY-MM-DD');
                end_dt = date_range.endDate.format('YYYY-MM-DD');
            }
            var filters = [{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            if(start_dt && end_dt){
                filters.push({ 'op': 'deq', 'field': 'created_at', 'data': start_dt+'<=>'+end_dt });
            }else{
                filters.push({ 'op': 'deq', 'field': 'created_at', 'data': moment().format('YYYY-MM-DD')+'<=>'+moment().format('YYYY-MM-DD') });
            }
            getFollowups(filters);
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
                self.dateRangeObj = picker;
                apply_filters();
            }}
        };

        // To load all records
        apply_filters();
        self.apply_filters = apply_filters;
    })
    .controller('ReportAppInstallsCtrl', function ReportAppInstallsCtrl($state, $stateParams, DashboardModel ) {
        var appInstallsCtrl = this;
        var data3 = [];
        var data4 = [];
        DashboardModel.getAppInstallStats()
            .then(function (data) {
                if(data){
                    appInstallsCtrl.app_installs_per_city = data.app_installs_per_city;
                    appInstallsCtrl.app_installs_per_brand = data.app_installs_per_brand;
                    appInstallsCtrl.bookings_by_status = data.bookings_by_status;
                    var i=0;
                    for(i=0; i< data.bookings_by_date.length;i++){
                        data3.push([new Date(data.bookings_by_date[i].label), data.bookings_by_date[i].count]);
                    }
                    for(i=0; i< data.app_installs_by_date.length;i++){
                        data4.push([new Date(data.app_installs_by_date[i].label), data.app_installs_by_date[i].count]);
                    }
                }else{
                    sweetAlert("Oops...", "Failed to Load App install stats", "error");
                }
            });

        var dataset = [
            {
                label: "App Installs",
                grow:{stepMode:"linear"},
                data: data4,
                color: "#1ab394",
                bars: {
                    show: true,
                    align: "center",
                    barWidth: 24 * 60 * 60 * 600,
                    lineWidth: 0
                }

            },
            {
                label: "Booking",
                grow:{stepMode:"linear"},
                data: data3,
                yaxis: 2,
                color: "#1C84C6",
                lines: {
                    lineWidth: 1,
                    show: true,
                    fill: true,
                    fillColor: {
                        colors: [
                            {
                                opacity: 0.2
                            },
                            {
                                opacity: 0.2
                            }
                        ]
                    }
                }
            }
        ];

        var options = {
            grid: {
                hoverable: true,
                clickable: true,
                tickColor: "#d5d5d5",
                borderWidth: 0,
                color: '#d5d5d5'
            },
            colors: ["#1ab394", "#464f88"],
            tooltip: true,
            xaxis: {
                mode: "time",
                tickSize: [3, "day"],
                tickLength: 0,
                axisLabel: "Date",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Arial',
                axisLabelPadding: 10,
                color: "#d5d5d5"
            },
            yaxes: [
                {
                    position: "left",
                    //max: 1070,
                    color: "#d5d5d5",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Arial',
                    axisLabelPadding: 3
                },
                {
                    position: "right",
                    color: "#d5d5d5",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: ' Arial',
                    axisLabelPadding: 67
                }
            ],
            legend: {
                noColumns: 1,
                labelBoxBorderColor: "#d5d5d5",
                position: "nw"
            }

        };

        function gd(year, month, day) {
            return new Date(year, month - 1, day).getTime();
        }

        /**
         * Definition of variables
         * Flot chart
         */
        appInstallsCtrl.flotData = dataset;
        appInstallsCtrl.flotOptions = options;
    })
    .controller('ReportBookingByUsersCtrl', function ReportBookingByUsersCtrl($state, $stateParams, CommonService ) {
        var self = this;

        self.filters = {};
        self.dateRangeObj = null;

        function format_data_for_dd(data, param_to_check){
            var formatted_list = [];
            for(var i=0;i<data.length;i++){
                if(data[i][param_to_check]){
                    formatted_list.push(data[i]);
                }
            }
            return formatted_list;
        }
        CommonService.getAdsData('report_booking_by_users')
            .then(function (data) {
                if(data){
                    self.utm_source_list = format_data_for_dd(data.utm_source, 'utm_source');
                    self.utm_medium_list = format_data_for_dd(data.utm_medium, 'utm_medium');
                    self.utm_campaign_list = format_data_for_dd(data.utm_campaign, 'utm_campaign');
                }else{
                    sweetAlert("Oops...", "Failed to Report", "error");
                }
            });

        function getBookingsSummary(filters){
            CommonService.getReportData('report_booking_by_users', filters)
                .then(function (data) {
                    if(data){
                        self.users_bookings_data = data.rows && data.rows.length?data.rows[0]:{};
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }

        function getPastBookingsSummary(filters){
            CommonService.getReportData('report_booking_by_users', filters)
                .then(function (data) {
                    if(data){
                        self.past_users_bookings_data = data.rows && data.rows.length?data.rows[0]:{};
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }
        function apply_filters(){
            var dateRangeObj = self.dateRangeObj;
            var date_range = dateRangeObj? dateRangeObj: self.filters.date;
            var start_dt = '';
            var past_start_dt = '';
            var end_dt = '';
            var past_end_dt = '';
            self.past_start_dt = '';
            self.past_end_dt = '';

            if(date_range){
                start_dt = date_range.startDate.format('YYYY-MM-DD');
                end_dt = date_range.endDate.format('YYYY-MM-DD');

                if(date_range.chosenLabel == 'Today'){
                    past_start_dt = moment().subtract(1, 'days');
                    past_end_dt = moment().subtract(1, 'days');

                }else if(date_range.chosenLabel == 'Yesterday'){
                    past_start_dt = moment().subtract(2, 'days');
                    past_end_dt = moment().subtract(2, 'days');

                }else if(date_range.chosenLabel == 'Last 7 Days'){
                    past_start_dt = moment().subtract(14, 'days');
                    past_end_dt = moment().subtract(7, 'days');

                }else if(date_range.chosenLabel == 'Last 30 Days'){
                    past_start_dt = moment().subtract(60, 'days');
                    past_end_dt = moment().subtract(30, 'days');

                }else if(date_range.chosenLabel == 'This Month'){
                    past_start_dt = moment().subtract(1, 'month').startOf('month');
                    past_end_dt = moment().subtract(1, 'month').endOf('month');

                }else if(date_range.chosenLabel == 'Last Month'){
                    past_start_dt = moment().subtract(2, 'month').startOf('month');
                    past_end_dt = moment().subtract(2, 'month').endOf('month');
                }
            }
            var filters = [];
            var past_filters = [];

            if(self.filters.booking_type){
                filters.push({ 'op': 'eq', 'field': 'booking_type', 'data': self.filters.booking_type });
                past_filters.push({ 'op': 'eq', 'field': 'booking_type', 'data': self.filters.booking_type });
            }
            if(self.filters.utm_source && self.filters.utm_source.utm_source !="?" && self.filters.utm_source.utm_source !== ""){
                filters.push({ 'op': 'eq', 'field': 'utm_source', 'data': self.filters.utm_source.utm_source });
                past_filters.push({ 'op': 'eq', 'field': 'utm_source', 'data': self.filters.utm_source.utm_source });
            }
            if(self.filters.utm_medium && self.filters.utm_medium.utm_medium !="?" && self.filters.utm_medium.utm_medium !== ""){
                filters.push({ 'op': 'eq', 'field': 'utm_medium', 'data': self.filters.utm_medium.utm_medium });
                past_filters.push({ 'op': 'eq', 'field': 'utm_medium', 'data': self.filters.utm_medium.utm_medium });
            }
            if(self.filters.utm_campaign && self.filters.utm_campaign.utm_campaign !="?" && self.filters.utm_campaign.utm_campaign !== ""){
                filters.push({ 'op': 'eq', 'field': 'utm_campaign', 'data': self.filters.utm_campaign.utm_campaign });
                past_filters.push({ 'op': 'eq', 'field': 'utm_campaign', 'data': self.filters.utm_campaign.utm_campaign });
            }
            if(start_dt && end_dt){
                filters.push({ 'op': 'deq', 'field': 'user_join_dt', 'data': start_dt+'<=>'+end_dt });
                if(past_start_dt && past_end_dt){
                    past_filters.push({ 'op': 'deq', 'field': 'user_join_dt', 'data': past_start_dt.format('YYYY-MM-DD')+'<=>'+past_end_dt.format('YYYY-MM-DD') });
                    self.past_start_dt = past_start_dt.format('YYYY-MM-DD');
                    self.past_end_dt = past_end_dt.format('YYYY-MM-DD');
                }
            }
            getBookingsSummary(filters);
            if(past_start_dt){
                getPastBookingsSummary(past_filters);
            }
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
                self.dateRangeObj = picker;
                apply_filters(picker);
            }}
        };


        // To load al records
        getBookingsSummary();
        self.apply_filters = apply_filters;
    })
    .controller('ReportBookingStatusSummaryCtrl', function ReportBookingStatusSummaryCtrl(CommonService){
        var self = this;

        function getBookingStatusSummary(filters){
            CommonService.getReportData('report_booking_in_status', filters)
                .then(function (data) {
                    if(data){
                        self.bookingStatusdata = data.rows;
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }
        getBookingStatusSummary();

    })
    .controller('ReportInquiryStatusSummaryCtrl', function ReportInquiryStatusSummaryCtrl(CommonService){
        var self = this;

        function getInquiryStatusSummary(filters){
            CommonService.getReportData('report_user_inquiry_in_status', filters)
                .then(function (data) {
                    if(data){
                        self.InquiryStatusdata = data.rows;
                    }else{
                        sweetAlert("Oops...", "Failed to Report", "error");
                    }
                });
        }
        getInquiryStatusSummary();

    })

;