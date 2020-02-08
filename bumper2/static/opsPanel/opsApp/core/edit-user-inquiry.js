/**
 * Created by Indy on 22/05/17.
 */
angular.module('ops.views.editUserInquiry',[
    'ops.services.common',
    'ops.services.user',
    'ops.services.booking',
    'ops.services.data'
]).controller('EditUserInquiryCtrl', function(CommonService,$scope,UserService,BOOKING_EVENTS,$rootScope, BookingService, $stateParams,DataService){
    var self = this;
    self.editedInquiry = null;
    self.selectedCar = null;
    self.selectedCarId = null;
    self.followups = null;
    self.userInquiryId = $stateParams.userInquiryId;
    self.newFollowup = {};

    $rootScope.$on(BOOKING_EVENTS.LoadFollowupInquiry, function () {
        console.log("data updated");
        loadData();
        loadFollowup();
    });

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
    $( document ).ready(function() {
        if(connection === null && user.user_detail){
            xmpp_connect();
        }
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
            $scope.baseCtrl.addCallNotes(2,self.userInquiryId);
            // addCallNotes();
        }
    }
    function xmpp_connect(click){
        var ongoingCall = DataService.getFollowupDataFromLocal();
        if(user.user_detail){
            if(ongoingCall && click){
                sweetAlert("info", "Please submit  previous call followup", "info");
            }
            else{
                if(self.presence){
                    var d = new Date();
                    var msg_gen_time =  d.getFullYear() + "-" +
                        ("00" + (d.getMonth() + 1)).slice(-2) + "-" +
                        ("00" + d.getDate()).slice(-2) + " " +
                        ("00" + d.getHours()).slice(-2) + ":" +
                        ("00" + d.getMinutes()).slice(-2) + ":" +
                        ("00" + d.getSeconds()).slice(-2);

                    var message = JSON.stringify({
                        module_id : 0,
                        cre_id : self.creId,
                        car_id : "",
                        call_id : self.userInquiryId,
                        lead_id : self.userInquiryId,
                        customer_id :self.editedInquiry.user.phone,
                        mobile : self.editedInquiry.user.phone,
                        name : self.editedInquiry.user.name,
                        process : '',
                        car_reg_num : "",
                        car_details : "",
                        msg_gen_time : msg_gen_time
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
                            connection.register.fields.username = user.id +'_'+ user.ops_phone +'_'+ user.user_detail.imei_no;
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

    CommonService.getCities().then(function(res){
        self.cities = res;
    });

    CommonService.getMasterData().then(function(res){
        self.userSources = res.new_sources;
        self.inquiryStatuses = res.user_inquiry_statuses;
        self.followupCommModes = res.followup_comm_modes;
        self.followupResults = res.followup_results;
        loadFollowup();
    });

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

    function loadData(){
        UserService.getUserInquiryById(self.userInquiryId)
            .then(function (data) {
                data.status = ''+ (data.status?data.status:'');
                data.lead_quality = ''+ data.lead_quality;
                data.city =  data.city ? '' + data.city:null;
                data.selectedCarId = data.car_model? data.car_model: null;
                self.editedInquiry = data;
                self.editedInquiry.user.formatedPhone = UserService.getCustomerNumber(self.editedInquiry.user.phone);
                self.selected_assigned_to = {'id': self.editedInquiry.assigned_to};
            });
    }

    function loadFollowup(){
        UserService.getUserInquiryFollowups(self.userInquiryId).then(function(res){
            self.next_followup_dt = res && res[0]?res[0].next_followup_dt:'';
            self.followups = res;
            for(var i=0; i< self.followups.length; i++){
                self.followups[i].comm_mode = self.followups[i].comm_mode ? self.followupCommModes[self.followups[i].comm_mode]:'';
            }
        });
    }

    loadData();

    function updateUserInquiry(){
        if(self.selectedCarId){
            self.editedInquiry.car_model_id = self.selectedCarId;
        }
        self.editedInquiry.assigned_to = self.selected_assigned_to.id != '?' ?self.selected_assigned_to.id:'';
        self.editedInquiry.lead_quality = self.editedInquiry.lead_quality ? parseInt(self.editedInquiry.lead_quality) : null;

        //console.log('To Save self.editedInquiry', self.editedInquiry);

        UserService.updateUserInquiry(self.userInquiryId, self.editedInquiry)
            .then(function (data) {
                self.ajax_loading = false;
                sweetAlert("success", "Inquiry Updated", "success");
                loadData();
            });
    }

    function addFollowup() {
        self.ajax_loading = true;
        var data = {
            'followup': [{
                "note": self.newFollowup.notes,
                "result": self.newFollowup.result && self.newFollowup.result.id != '?' ? self.newFollowup.result.id: null,
                "comm_mode": self.newFollowup.comm_mode,
                "next_followup_dt":  self.newFollowup.next_followup_dt
            }]
        };
        if(self.newFollowup.result.action_type == 1 && moment(self.newFollowup.next_followup_dt) < moment.now()){
            sweetAlert("Error", "Next Followup date should be greater than now.", "error");
            self.ajax_loading = false;
            return false;
        }

        UserService.saveUserInquiryFollowups(self.userInquiryId, data)
            .success(function(response){
                self.ajax_loading = false;
                self.showfollowup = false;
                self.newFollowup = {};
                loadFollowup();
                sweetAlert("success", "Followup Saved", "success");
            })
            .error(function(response){
                self.ajax_loading = false;
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

    self.setSelectedCar = setSelectedCar;
    self.getModel = getModel;
    self.updateUserInquiry = updateUserInquiry;
    self.addFollowup = addFollowup;
    self.sendMessage =sendMessage;
    self.xmpp_connect = xmpp_connect;

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