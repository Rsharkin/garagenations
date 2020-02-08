/**
 * Created by Indy on 15/02/17.
 */
angular.module('ops.views.editBookingSummary', [
    'ops.services.booking',
    'ops.services.user',
    'ops.services.common',
    'ops.services.data'
])
    .controller('EditBookingSummaryCtrl', function EditBookingSummaryCtrl($state,$rootScope, $scope, BOOKING_EVENTS, BookingService, UserService,
                                                                          $uibModal, CommonService, DataService){
        var self = this;

        self.ajax_loading = false;
        self.editedBooking = null;
        self.errorMsg = '';
        self.save_and_continue = false;
        $rootScope.$on(BOOKING_EVENTS.LoadFollowupBooking, function () {
           updateBookingData();
           loadFollowup();
           $scope.$emit('bookingChanged','');
        });
        self.followups = null;
        self.presence = false;
        var user = UserService.getCurrentUser();
        if(user.user_detail){
            self.imei =  user.user_detail.imei_no;
            self.creId = user.user_detail.cre_id;
        }
        var connection = null;
        var xmpp_server = 'xmpp.ninjacrm.com';
        var BOSH_SERVICE = 'https://'+xmpp_server+'/http-bind';
        var jid = self.imei+'@'+xmpp_server;
        self.booking = BookingService.getCurrentBooking();
        //console.log("booking",self.booking);
        UserService.getUserById(self.booking.user).then(function (results) {
            self.bookingUser= results;
            //console.log("self.bookingUser",self.bookingUser);
            $( document ).ready(function() {
                if(connection === null && user.user_detail){
                    xmpp_connect();
                }
            });
        });
        $(window).bind("beforeunload", function() {
            xmpp_disconnect();
        });
        function onSubscriptionRequest(stanza) {
            //console.log("stanza",stanza);
            if (stanza.getAttribute("type") == "subscribe") {
                var from = $(stanza).attr('from');
                //console.log('onSubscriptionRequest: from=' + from);
                // Send a 'subscribed' notification back to accept the incoming
                // subscription request
                connection.send($pres({
                    to: from,
                    type: "subscribed"
                }));
            }
            return true;
        }
        function subscribePresence(jid) {
            //console.log('subscribePresence: ' + jid);
            connection.send($pres({
                to: jid,
                type: "subscribe"
            }));
        }
        function onPresence(presence) {
            //console.log('onPresence:');
            var ongoingCall = DataService.getFollowupDataFromLocal();

            var presence_type = $(presence).attr('type');
            //console.log("subscriber presence",presence_type);// unavailable, subscribed, etc...
            var from = $(presence).attr('from'); // the jabber_id of the contact
            from_jid = from.split('/')[0];
            if (!presence_type) presence_type = "online";
            console.log(presence);
            console.log(' >' + from_jid + ' --> ' + presence_type);
            if(from_jid == jid){
                if (presence_type === 'unavailable' || presence_type === 'error') {
                    self.presence = false;
                    $('#call-status').removeClass().addClass("btn-danger").addClass("btn-xs").addClass("pull-right").text('Not Connected');
                } else {
                    $('#call-status').removeClass().addClass('btn-primary').addClass("btn-xs").addClass("pull-right").text('Ready to Call');
                    self.presence = true;
                }

            }
            else{
                $('#call-status').removeClass().addClass("btn-danger").addClass("btn-xs").addClass("pull-right").text('Open NINJA CRM App');
                self.presence = false;
            }
            return true;
        }
        function sendMessage(to_jid, message) {
            console.log("message", message);
            if(message && to_jid){
                var reply = $msg({
                    to: to_jid,
                    type: 'chat'
                })
                    .cnode(Strophe.xmlElement('body', message))
                    .up()
                    .c('active', {xmlns: "http://jabber.org/protocol/chatstates"});
                connection.send(reply);
                $scope.baseCtrl.addCallNotes(1,self.booking.id);
            }
        }
        function xmpp_connect(click){
            var ongoingCall = DataService.getFollowupDataFromLocal();
            if(user.user_detail){
                if(ongoingCall && click) {
                    sweetAlert("info", "Please submit previous call followup", "info");
                }
                else{
                    if (self.presence) {
                        var d = new Date();
                        var msg_gen_time = d.getFullYear() + "-" +
                            ("00" + (d.getMonth() + 1)).slice(-2) + "-" +
                            ("00" + d.getDate()).slice(-2) + " " +
                            ("00" + d.getHours()).slice(-2) + ":" +
                            ("00" + d.getMinutes()).slice(-2) + ":" +
                            ("00" + d.getSeconds()).slice(-2);

                        var message = JSON.stringify({
                            module_id: 0,
                            cre_id: self.creId,
                            car_id: self.booking.usercar,
                            call_id: self.booking.id,
                            lead_id: self.booking.id,
                            customer_id: self.booking.user,
                            mobile: self.bookingUser.phone,
                            name: self.bookingUser.name,
                            process: '',
                            car_reg_num: "",
                            car_details: "",
                            msg_gen_time: msg_gen_time
                        });
                        sendMessage(jid, message);
                    }
                    else {
                        if (BOSH_SERVICE) {
                            connection = new Strophe.Connection(BOSH_SERVICE);
                        }
                        //console.log("connection", connection);
                        connection.register.connect(xmpp_server, function (status) {
                            //console.log("status", status);
                            //console.log("strophe status R", Strophe.Status.REGISTER);
                            if (status === Strophe.Status.REGISTER) {
                                connection.register.fields.username = user.id + '_' + user.ops_phone + '_' + user.user_detail.imei_no;
                                connection.register.fields.password = "bumper@321";
                                //console.log(connection.register.fields);
                                connection.register.submit();
                            } else if (status === Strophe.Status.REGISTERED || status === Strophe.Status.CONFLICT) {
                                //console.log('login');
                                connection.authenticate();
                            } else if (status === Strophe.Status.NOTACCEPTABLE) {
                                //console.log("Registration form not properly filled out.");
                            } else if (status === Strophe.Status.REGIFAIL) {
                                // console.log("The Server does not support In-Band Registration");

                            } else if (status === Strophe.Status.CONNECTED) {
                                //console.log('logged in');
                                //make call button active
                                connection.send($pres());
                                subscribePresence(jid);
                                // set handlers
                                connection.addHandler(onSubscriptionRequest, null, "presence", "subscribe");
                                connection.addHandler(onPresence, null, "presence");
                                // send message
                            } else if (status === Strophe.Status.DISCONNECTED) {
                                connection = null;
                                //console.log("unable to connect");
                            } else {
                                //console.log("callback status " + status);
                            }

                        });
                    }
                }
            }else{
                sweetAlert("Error", "Please Upadate Your Imei Number in Records", "error");
            }
        }
        function xmpp_disconnect(){
            if(connection && connection.connected === true){
                connection.options.sync = true;
                connection.flush();
                connection.disconnect();
            }
        }
        function returnToBookings(){
            $state.go('base.bookings',{});
        }
        function cancelEditing(){
            returnToBookings();
        }
        CommonService.getMasterData(self.booking.city).then(function(res){
            self.bookingSources = res.new_sources;
            self.followupCommModes = res.followup_comm_modes;
            self.cancellationReasons = res.cancellation_reasons;
            self.typeOfWorks = res.type_of_works;
            self.selectedCancellationReason = _.find(self.cancellationReasons,{'id':self.booking.cancel_reason_dd});
            self.selectedFinalCancelReason = _.find(self.cancellationReasons,{'id':self.booking.final_cancel_reason});
            loadFollowup();
            loadRework();
        });

        CommonService.getCities().then(function(res){
            self.cities = res;
        });

        function loadRework(){
            // load rework
            BookingService.getReworkOnBooking(self.booking.id).then(function(response){
                self.reworks = response;
                if(self.reworks.rework_panels.length>0 || self.reworks.rework_packages.length>0){
                    $scope.editBookingCtrl.hasRework = true;
                }
                for(var i=0; i<self.reworks.rework_panels.length; i++){
                    self.reworks.rework_panels[i].type_of_work = self.typeOfWorks[self.reworks.rework_panels[i].type_of_work];
                }
            });
        }

        function loadData(){
            self.editedBooking = {
                'id': self.booking.id,
                'assigned_to': self.booking.assigned_to ? '' + self.booking.assigned_to:null,
                'caller': self.booking.caller ? '' + self.booking.caller:null,
                'next_followup': self.booking.next_followup,
                'source': self.booking.source,
                'is_doorstep': self.booking.is_doorstep,
                'lead_quality': self.booking.lead_quality ? '' + self.booking.lead_quality:null,
                'city': self.booking.city ? '' + self.booking.city:null
            };

            self.existing_package_price_list = [];

            for(var i=0; i< self.booking.booking_package.length; i++){
                self.existing_package_price_list.push(self.booking.booking_package[i].package);
            }
            self.selectedCancellationReason = _.find(self.cancellationReasons,{'id':self.booking.cancel_reason_dd});
            self.selectedFinalCancelReason = _.find(self.cancellationReasons,{'id':self.booking.final_cancel_reason});

            var denting_package = _.find(self.booking.booking_package,{'package':{'package':{'category':2}}});

            self.existing_panel_list = [];
            if(denting_package){
                self.existing_panel_list = _.reduce(denting_package.booking_package_panel, function(result, value, key) {
                    result.push(value.panel_details.car_panel.id);
                    return result;
                }, []);
            }

            self.showNextFollowupDtEditBtn = false;
        }

        function updateBookingData(){
            self.booking = BookingService.getCurrentBooking();
            loadData();
            loadRework();
        }

// listen for the event in the relevant $scope
        $scope.$on('bookingUpdated', function (event, data) {
            updateBookingData();
        });

        loadData();

        function loadFollowup(){
            BookingService.getBookingFollowups(self.booking.id).then(function(res){
                self.followups = res;
                for(var i=0; i< self.followups.length; i++){
                    self.followups[i].comm_mode = self.followups[i].comm_mode ? self.followupCommModes[self.followups[i].comm_mode]:'';
                }
            });
        }

        UserService.getOpsAgents().then(function(res){
            self.opsAgents = res;
        });

        function saveBooking(do_continue){
            self.ajax_loading = true;

            BookingService.saveBooking(self.booking.id, self.editedBooking)
                .success(function (response){
                    self.ajax_loading = false;
                    sweetAlert("success", "Booking Saved", "success");
                    if(!do_continue){
                        returnToBookings();
                    }else{
                        $scope.$emit('bookingChanged','');
                    }
                })
                .error(function(response){
                    var status = response.status;
                    if(status == '401'){
                        sweetAlert("Error", "You don't have permission required to do this action.", "error");
                    }else if(status == '400'){
                        self.errorMsg = 'Please make sure all values are correctly filled: ' + response.data.data[0];
                    }else{
                        sweetAlert("Error", "Errors: Server Error.", "error");
                    }
                })
            ;
        }

        function addFollowup() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-booking-followup.html',
                controller: FollowupModalInstanceCtrl,
                controllerAs: 'followupModalCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    booking_caller: function () {
                        return self.booking.caller;
                    },
                    bookingCity: function (){
                        return self.booking.city;
                    }
                }
            });
            modalInstance.result.then(function () {
                loadFollowup();
                $scope.$emit('bookingChanged','');
            });
        }
        function addCallNotes() {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-call-notes.html',
                controller: CallNotesModalController,
                controllerAs: 'callNotesCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    bookingCity: function (){
                        return self.booking.city;
                    }
                }
            });
            modalInstance.result.then(function () {
                loadFollowup();
                $scope.$emit('bookingChanged','');
            });
        }

        function setCancellationReason(actionToSet) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/cancel-booking.html',
                controller: SetCancellationReasonModalInstanceCtrl,
                controllerAs: 'setCRCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    cancellationReasons: function () {
                        return self.cancellationReasons;
                    },
                    actionToSet: function () {
                        return actionToSet;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function setLostReason(actionToSet) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/mark-booking-lost.html',
                controller: SetLostReasonModalInstanceCtrl,
                controllerAs: 'setCRCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    cancellationReasons: function () {
                        return self.cancellationReasons;
                    },
                    actionToSet: function () {
                        return actionToSet;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function addPackageToBooking(isExtra) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-package-to-booking.html',
                controller: AddPackageModalInstanceCtrl,
                controllerAs: 'addPackageCtrl',
                resolve: {
                    bookingId: function () {
                        return self.booking.id;
                    },
                    usercarId: function () {
                        return self.booking.usercar;
                    },
                    existingPackagePriceList: function () {
                        return self.existing_package_price_list;
                    },
                    isExtra:function (){
                        return isExtra;
                    },
                    bookingCity:function (){
                        return self.booking.city;
                    }
                }
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function addPanelToPackage(bookingPackageId, userCarId, isExtra) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-panel-to-package.html',
                controller: AddPanelToPackageModalInstanceCtrl,
                controllerAs: 'addPanelToPackageCtrl',
                resolve: {
                    bookingPackageId: function () {
                        return bookingPackageId;
                    },
                    userCarId: function () {
                        return userCarId;
                    },
                    existingPanelList: function () {
                        return self.existing_panel_list;
                    },
                    existingPackages: function () {
                        return self.existing_package_price_list;
                    },
                    isExtra:function (){
                        return isExtra;
                    },
                    bookingCity:function (){
                        return self.booking.city;
                    }
                },
                size:'lg'
            });

            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function addReworkPanel(bookingPackagePanel) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-panel-rework.html',
                controller: AddReworkPanelModalInstanceCtrl,
                controllerAs: 'addReworkPanelModalInstanceCtrl',
                resolve: {
                    bookingPackagePanel: function () {
                        return bookingPackagePanel;
                    },
                    bookingCity: function(){
                        return self.booking.city;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function removeReworkPanel(rework_panel_id) {
            swal(
                {
                    title: "Remove Rework Panel?",
                    text: "Are you sure? This is not reversible.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Remove It!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: true
                },
                function(){
                    BookingService.removeReworkPanelFromBooking(rework_panel_id).then(function(result){
                        $scope.$emit('bookingChanged','');
                    });
                });
        }

        function addReworkPackage(bookingPackage) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/add-package-rework.html',
                controller: AddReworkPackageModalInstanceCtrl,
                controllerAs: 'addReworkPackageModalInstanceCtrl',
                resolve: {
                    bookingPackage: function () {
                        return bookingPackage;
                    }
                }
            });
            modalInstance.result.then(function () {
                $scope.$emit('bookingChanged','');
            });
        }

        function removeReworkPackage(rework_package_id) {
            swal(
                {
                    title: "Remove Rework Package?",
                    text: "Are you sure? This is not reversible.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Remove It!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: true
                },
                function(){
                    BookingService.removeReworkPackageFromBooking(rework_package_id).then(function(result){
                        $scope.$emit('bookingChanged','');
                    });
                });
        }

        function createReworkBooking(){
            swal(
                {
                    title: "Are you sure?",
                    text: "This will create a booking with same user, user car and other details as empty.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Create it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.createBooking({
                            'user_id': self.booking.user,
                            'usercar': self.booking.usercar,
                            'city': self.booking.city,
                            'source': 'rework',
                            'rework_booking': self.booking.id
                        }
                    ).then(function(result){
                        $scope.$emit('bookingChanged','');
                        swal(
                            {
                                title: "Rework Booking Created: " + result.data.id,
                                text: "New created booking does not have panel or packages.",
                                type: "success",
                                showCancelButton: true,
                                confirmButtonColor: "#DD6B55",
                                confirmButtonText: "Take me to it!",
                                showLoaderOnConfirm: true,
                                closeOnConfirm: true
                            },
                            function(){
                                $state.go('base.bookings.editBooking', {'bookingId': result.data.id});
                            });

                    });
                });
        }

        function updateTypeOfWork(bookingPackageId,userCarId,panelId) {
            var modalInstance = $uibModal.open({
                templateUrl: 'views/booking_type_of_work_change.html',
                controller: TypeOfWorkChangeModalInstanceCtrl,
                controllerAs: 'typeOfWorkCtrl',
                resolve: {
                    bookingPackageId: function () {
                        return bookingPackageId;
                    },
                    userCarId: function () {
                        return userCarId;
                    },
                    panelId: function () {
                        return panelId;
                    },
                    bookingCity: function () {
                        return self.booking.city;
                    }
                },
                size:'lg'
            });
            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }

        function removePackageFromBooking(bookingPackageId){
            swal(
                {
                    title: "Are you sure?",
                    text: "Removing package cannot be un-done, Also if last package is removed then booking will be closed!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Remove it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.removePackageFromBooking(bookingPackageId).then(function(result){
                        if(result == 'removed'){
                            sweetAlert("success", "Package removed", "success");
                            $scope.$emit('bookingChanged','');
                        }
                    });
                });
        }

        function removePanelFromPackage(bookingPanelId){
            swal(
                {
                    title: "Are you sure?",
                    text: "Removing panel cannot be un-done!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Remove it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.removePanelFromPackage(bookingPanelId).then(function(result){
                        if(result == 'removed'){
                            sweetAlert("success", "Panel removed", "success");
                            $scope.$emit('bookingChanged','');
                        }
                    });
                });
        }

        function markBookingClosed(){
            swal(
                {
                    title: "Are you sure?",
                    text: "You will not be able to undo this or take any other action!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, close it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.saveBooking(self.booking.id,{},23).then(function(response){
                        swal("Closed!", "Booking has been closed.", "success");
                        $scope.$emit('bookingChanged','');
                    });

                });
        }

        function requestFeedback(){
            swal(
                {
                    title: "Are you sure?",
                    text: "A Notification will be sent to customer!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, send it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.saveBooking(self.booking.id,{},53).then(function(response){
                        swal("Sent!", "Notification Queued in server.", "success");
                    });

                });
        }

        function alertBookingChanged(){
            swal(
                {
                    title: "Are you sure?",
                    text: "Email, SMS & push notifications will be sent to customer!!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, send it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.alertBookingChanged(self.booking.id)
                        .success(function(response){
                            swal("Booking Alert Sent!", "Notifications Sent.", "success");
                        })
                        .error(function(response){
                            sweetAlert("Error", response.message, "error");

                        })
                    ;
                });
        }

        function updatePanelPrice(bookingPackageId,selectedPanelId,newPriceForPanel, extra){
            if(!newPriceForPanel){
                sweetAlert("Error", "Please enter all prices.", "error");
                return false;
            }

            BookingService.updatePanelToPackage(bookingPackageId, selectedPanelId, newPriceForPanel, extra)
                .success(function(response){
                    self.ajax_loading = false;
                    sweetAlert("success", "Panel Updated", "success");
                    $scope.$emit('bookingChanged','');
                })
                .error(function(response){
                    self.ajax_loading = false;
                    self.errorMsg = 'Something went wrong on server.';

                    if(response.detail){
                        self.errorMsg = response.detail;
                    }
                    else if(response.non_field_errors){
                        self.errorMsg = 'This panel has already been added';
                    }else{
                        self.errorMsg = 'Please make sure all values are correctly filled.';
                    }
                    sweetAlert("Error", self.errorMsg, "error");
                });
        }

        function setOpsStatusToFollowup(){
            var actionToSet = null;
            if(self.booking.status.id == 1){
                actionToSet = 109;
            }else if(self.booking.status.id == 3){
                actionToSet = 108;
            }else if(self.booking.status.id == 26){
                actionToSet = 111;
            }

            if(actionToSet){
                swal(
                    {
                        title: "Are you sure?",
                        text: "Ops status of booking will be changed to Followup.",
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Yes, do it!",
                        showLoaderOnConfirm: true,
                        closeOnConfirm: false
                    },
                    function(){
                        BookingService.saveBooking(self.booking.id,{},actionToSet).then(function(response){
                            swal("Closed!", "Ops Status Set to Following-Up.", "success");
                            $scope.$emit('bookingChanged','');
                        });
                    });
            }
        }

        function removeOpsStatusFromFollowup(){
            var actionToSet = null;
            if(self.booking.status.id == 1){
                actionToSet = 151;
            }else if(self.booking.status.id == 3){
                actionToSet = 152;
            }else if(self.booking.status.id == 26){
                actionToSet = 153;
            }

            if(actionToSet){
                swal(
                    {
                        title: "Are you sure?",
                        text: "Ops status of booking will be cleared.",
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Yes, do it!",
                        showLoaderOnConfirm: true,
                        closeOnConfirm: false
                    },
                    function(){
                        BookingService.saveBooking(self.booking.id,{},actionToSet).then(function(response){
                            swal("Closed!", "Ops Status cleared", "success");
                            $scope.$emit('bookingChanged','');
                        });
                    });
            }
        }

        function markCarReturnedByCustomerBooking(){
            swal(
                {
                    title: "Rework?",
                    text: "This will set booking into 'Car Returned by Customer' status.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Do it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.saveBooking(self.booking.id,{}, 143).then(function(result){
                        $scope.$emit('bookingChanged','');
                        swal("Done!", "Car Being returned by customer.", "success");
                    });
                });
        }

        function sendEmail() {
            swal(
                {
                    title: "Are you sure?",
                    text: "A Notification will be sent to customer!",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, send it!",
                    showLoaderOnConfirm: true,
                    closeOnConfirm: false
                },
                function(){
                    BookingService.saveBooking(self.booking.id,{},59).then(function(response){
                        swal("Sent!", "Notification Queued in server.", "success");
                    });
                });
        }

        function showQuotes(bookingPackagePanelId, panelName){
            var modalInstance = $uibModal.open({
                templateUrl: 'views/part-docs-for-panel.html',
                controller: partDocForPanelModalInstanceCtrl,
                controllerAs: 'partDocPanelDetailsCtrl',
                resolve: {
                    bookingPackagePanelId: function () {
                        return bookingPackagePanelId;
                    },
                    booking: function () {
                        return self.booking;
                    },
                    panelName: function () {
                        return panelName;
                    }
                },
                size:'lg'
            });

            modalInstance.result.then(function () {
                // firing an event upwards
                $scope.$emit('bookingChanged','');
            });
        }
        self.sendMessage =sendMessage;
        self.xmpp_connect = xmpp_connect;
        self.saveBooking = saveBooking;
        self.addFollowup = addFollowup;
        self.addPackageToBooking = addPackageToBooking;
        self.removePackageFromBooking = removePackageFromBooking;
        self.addPanelToPackage = addPanelToPackage;
        self.removePanelFromPackage = removePanelFromPackage;
        self.cancelEditing = cancelEditing;
        self.setCancellationReason = setCancellationReason;
        self.setLostReason = setLostReason;
        self.markBookingClosed = markBookingClosed;
        self.updatePanelPrice = updatePanelPrice;
        self.alertBookingChanged = alertBookingChanged;
        self.setOpsStatusToFollowup = setOpsStatusToFollowup;
        self.removeOpsStatusFromFollowup = removeOpsStatusFromFollowup;
        self.requestFeedback = requestFeedback;
        self.sendEmail = sendEmail;
        self.updateTypeOfWork =updateTypeOfWork;
        self.addReworkPanel =addReworkPanel;
        self.addReworkPackage =addReworkPackage;
        self.createReworkBooking =createReworkBooking;
        self.removeReworkPanel =removeReworkPanel;
        self.removeReworkPackage =removeReworkPackage;
        self.markCarReturnedByCustomerBooking = markCarReturnedByCustomerBooking;
        self.showQuotes = showQuotes;

        var datePicker = jQuery(".form_datetime").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            autoclose: true,
            todayBtn: true,
            startDate: "2015-07-01 10:00",
            minuteStep: 5,
            orientation: 'auto'
        });
    });