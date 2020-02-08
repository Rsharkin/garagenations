/**
 * Created by Indy on 30/03/17.
 */
angular.module('ops.views.crewDashboard',[
    'ops.services.common',
    'ops.services.user'
])
    .controller('CrewDashCtrl', function($scope, CommonService, UserService, $uibModal){
        var self = this;
        self.timeline = null;
        var groups = [];
        var items = [];


        self.popup1 = {
            opened: false
        };

        self.dateOptions = {
            formatYear: 'yy',
            maxDate: new Date(2020, 5, 22),
            minDate: new Date(2015, 3, 1),
            startingDay: 1,
            showWeeks:false
            //showButtonBar: false
        };

        self.open1 = function() {
            self.popup1.opened = true;
        };

        self.dt = moment().toDate();
        self.dateToProcess = moment().format('YYYY-MM-DD');

        self.cities = CommonService.getSelectedCities();

        UserService.getDriverLocation().then(function(res){
            loadActiveDriverFullList(res);
        });

        function loadActiveDriverFullList(driverLocationList){
            UserService.getActiveDrivers().then(function(res){
                var i =0,
                    j =0;
                for(i=0;i<res.length;i++){
                    var driver_loc = _.find(driverLocationList,{'driver':res[i].id});
                    groups.push({
                        id: parseInt(res[i].id),
                        content: res[i].name + '<br>' + (driver_loc?('  <a  href="http://maps.google.com/maps?t=m&q=loc:'+driver_loc.latitude+'+'+driver_loc.longitude+'" target="_blank" title="Last location on Crew"><i class="fa fa-map-marker text-danger"></i></a> (Updated: '+ moment(driver_loc.updated_at).format('MMM-DD HH:mm') +')'):''),
                        order: i
                    });
                }
                loadBookings();
            });
        }

        function loadBookings(){
            var filters = [{ 'op': '2deqor', 'field': 'pickup_time<=>drop_time', 'data': self.dateToProcess },{ 'op': 'iin', 'field': 'city_id', 'data': self.cities.join() }];

            CommonService.getReportData('report_crew_dashboard_pickup', filters)
                .then(function (data) {
                    if(data){
                        var bookings = data.rows;
                        var startTimeSplit = [];
                        items = [];
                        var startTime = null;
                        var i = 0;
                        self.pickup_count = 0;
                        self.drop_count = 0;
                        for(i=0; i<bookings.length; i++){
                            if(bookings[i].pickup_date === self.dateToProcess){
                                bookings[i].action = 'Pick';
                                self.pickup_count += 1;
                            }
                            if(bookings[i].drop_date === self.dateToProcess){
                                if(bookings[i].action){
                                    bookings[i].action = 'Both';
                                    self.pickup_count += 1;
                                    self.drop_count += 1;
                                }else{
                                    bookings[i].action = 'Drop';
                                    self.drop_count += 1;
                                }
                            }

                            if(bookings[i].action === 'Both'){
                                // Add pickup block
                                startTimeSplit = bookings[i].pickup_time.split(':');
                                startTime = moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0});
                                items.push({
                                    id: i,
                                    content: 'Pick: <a href="/core/bookings/editBooking/' + bookings[i].booking_id + '/" target="_blank">' + bookings[i].booking_id + '</a> <b>'+ bookings[i].status +'</b> (From: ' + bookings[i].address1 + ', '+ bookings[i].address2 +'<br>  To: ' + bookings[i].workshop + ')',
                                    start:  moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0}),
                                    end:  startTime.add(2, 'h'),
                                    group: bookings[i].pickup_driver_id,
                                    type: 'range'
                                });
                                // Add drop block
                                startTimeSplit = bookings[i].drop_time.split(':');
                                startTime = moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0});
                                items.push({
                                    id: i+1000,
                                    content: 'Drop: <a href="/core/bookings/editBooking/' + bookings[i].booking_id + '/" target="_blank">' + bookings[i].booking_id + '</a> <b>'+ bookings[i].status +'</b> (From: ' + bookings[i].workshop + ' <br>  To: ' + bookings[i].drop_address1 + ', '+ bookings[i].drop_address2 +' )',
                                    start:  moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0}),
                                    end:  startTime.add(2, 'h'),
                                    group: bookings[i].drop_driver_id,
                                    type: 'range'
                                });

                            }else if(bookings[i].action === 'Pick'){
                                startTimeSplit = bookings[i].pickup_time.split(':');
                                startTime = moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0});
                                items.push({
                                    id: i,
                                    content: 'Pick: <a href="/core/bookings/editBooking/' + bookings[i].booking_id + '/" target="_blank">' + bookings[i].booking_id + '</a> <b>'+ bookings[i].status +'</b> (From: ' + bookings[i].address1 + ', '+ bookings[i].address2 +'<br>  To: ' + bookings[i].workshop + ')',
                                    start:  moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0}),
                                    end:  startTime.add(2, 'h'),
                                    group: bookings[i].pickup_driver_id,
                                    type: 'range'
                                });
                            }else if(bookings[i].action === 'Drop'){
                                startTimeSplit = bookings[i].drop_time.split(':');
                                startTime = moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0});
                                items.push({
                                    id: i,
                                    content: 'Drop: <a href="/core/bookings/editBooking/' + bookings[i].booking_id + '/" target="_blank">' + bookings[i].booking_id + '</a> <b>'+ bookings[i].status +'</b> (From: ' + bookings[i].workshop + ' <br>  To: ' + bookings[i].drop_address1 + ', '+ bookings[i].drop_address2 +' )',
                                    start:  moment().set({hour:startTimeSplit[0],minute:startTimeSplit[1],second:0}),
                                    end:  startTime.add(2, 'h'),
                                    group: bookings[i].drop_driver_id,
                                    type: 'range'
                                });
                            }
                        }
                        self.bookings = bookings;
                        loadTimeline();
                    }else{
                        sweetAlert("Oops...", "Failed to Load bookings", "error");
                    }
                });
        }

        function loadTimeline(){
            if(!self.timeline){
                var container = document.getElementById('visualization');
                var options = {
                    orientation: {axis: 'both'},
                    min: moment().set({hour:6,minute:0,second:0}),                // lower limit of visible range
                    max: moment().set({hour:23,minute:0,second:0}),                // upper limit of visible range
                    timeAxis: {scale: 'hour', step: 1},
                    zoomMin: 1000 * 60 * 60 * 2,             // in milliseconds at min level, i.e 2 hr
                    //zoomMax: 1000 * 60 * 60 * 24 * 31 * 3    // day in 2 hour slots
                };
                //var timeline = new vis.Timeline(container, items, groups, options);
                self.timeline = new vis.Timeline(container);
                self.timeline.setOptions(options);
                self.timeline.setItems(items);
                self.timeline.setGroups(groups);
            }else{
                self.timeline.setItems(items);
            }
        }

        function assignDriver(bookingId, driverFor) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/assign-driver.html',
                controller: AssignDriverModalInstanceCtrl,
                controllerAs: 'assignDriverCtrl',
                resolve: {
                    bookingId: function () {
                        return bookingId;
                    },
                    driver_for: function () {
                        return driverFor;
                    },
                    assignmentFor: function () {
                        return 'Driver';
                    },
                    actionToSet: function () {
                        return null;
                    }
                }
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                // $scope.$emit('bookingChanged','');
                loadBookings();
            });
        }

        function dateChanged(){
            self.dateToProcess = moment(self.dt).format('YYYY-MM-DD');
            loadBookings();
        }

        function requestUserLocation(){
            var user_id_list = [];
            for(var i=0;i<groups.length;i++){
                user_id_list.push(groups[i].id);
            }
            CommonService.requestUserLocation({'user_ids':user_id_list.join(',')}).then(function(response){
                sweetAlert("Success", "Request sent to crew app, updates will start coming soon.", "success");
            });
        }

        // listen for the event in the relevant $scope
        $scope.$on('baseFilterCitiesChanged', function (event, data) {
            self.cities = CommonService.getSelectedCities();
            loadBookings();
        });


        self.assignDriver = assignDriver;
        self.dateChanged = dateChanged;
        self.requestUserLocation = requestUserLocation;
    });