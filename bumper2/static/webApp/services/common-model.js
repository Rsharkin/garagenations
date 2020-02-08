/**
 * Created by inderjeet on 1/4/16.
 */

angular.module('bumper.services.common', [
])
    .service('CommonModel', function ($http, $q) {
        var model = this,
            URLS = {
                FETCH_CITIES: '/api/city/?format=json&limit=0',
                FETCH_CAR_MODEL: '/api/model/',
                FETCH_PACKAGE: '/api/package/?',
                FETCH_PANEL: '/api/panel-price/?format=json&limit=0',
                USER_CAR: '/api/usercar/',
                BOOKING_ENDPOINT: '/api/booking/',
                USER_ADDRESS: '/api/user-address/',
                BOOKING_ADDRESS: '/api/booking-address/',
                CITRUS_PAY: '/payment/citrus-pay-bill-gen-web/',
                BOOKING_BILL: '/api/booking-bill/',
                POPULAR_PACKAGES: 'api/package/?popular=True',
                PARTNER_LEAD_ENDPOINT: '/api/partner-lead/',
                CANCELLATION_REASONS: '/api/user/sync_user_details',
                USER_INQUIRY: '/api/user-inquiry/',
                DELETE_COUPON: '/api/booking-coupon/',
                PAYMENT_GATEWAY:'/api/v2/booking-bill/',
                GET_BOOKING_FROM_TOKEN:'/api/booking/get_booking_from_token/',
                INQUIRY_FROM_CHAT: '/api/user-inquiry/chat-inquiry/',
                BOOKING_FEEDBACK : '/api/booking-cust-feedback/',
                BOOKING_CHECKLIST:'/api/booking-checklist/',
                REFERRAL_CODE:'/api/referral-code/',
                JOBCARD_ENDPOINT:'/api/booking-jobcard/',
                PANEL_LIST:'/api/panel/?part_type=1&internal=false'
            };
        function fetch_from_api(url) {
            return $http.get(url).then(function (result) {
                return result.data;
            });
        }
        model.getCities = function () {
            return fetch_from_api(URLS.FETCH_CITIES);
        };
        model.getModel = function(brand_name){
            if (brand_name) {
                return fetch_from_api(URLS.FETCH_CAR_MODEL+"?search="+brand_name);
            } else {
                return fetch_from_api(URLS.FETCH_CAR_MODEL+"?popular=True");
            }
        };
        model.searchCars = function(searchText){
            if(searchText){
                return $http.get(URLS.FETCH_CAR_MODEL+"?search="+searchText).then(function(result){
                    return result.data.results?result.data:null;
                });
            }else{
                return $http.get(URLS.FETCH_CAR_MODEL+"?popular=True").then(function(result){
                    return result.data.results?result.data:null;
                });
            }
        };
        model.getPanel = function(carModel, cityId,size) {
            return fetch_from_api(URLS.FETCH_PANEL+"&carmodel_id="+carModel+"&city="+cityId+"&part_type=1"+"&size="+size);
        };
        model.getPart = function (carModel, cityId){
            return fetch_from_api(URLS.FETCH_PANEL+"&carmodel_id="+carModel+"&city="+cityId+"&part_type=2");
        };
        model.getPackage = function(cityId, modelId){
            return fetch_from_api(URLS.FETCH_PACKAGE+"&city="+cityId+"&car_model="+modelId);
        };
        model.createPackageBooking= function(package_details){
            return $http.post(URLS.BOOKING_ENDPOINT,package_details);
        };
        model.getFullBodyPackage=function (cityId,modelId) {
            return fetch_from_api(URLS.FETCH_PACKAGE+"city="+cityId+"&car_model="+modelId+"&category=3");
        };
        model.getDentingPackage= function (cityId,modelId) {
            return fetch_from_api(URLS.FETCH_PACKAGE+"city="+cityId+"&car_model="+modelId+"&category=2");
        };
        model.saveUserCar=function (model_id,year) {
            if(year) {
                return $http.post(URLS.USER_CAR, {'car_model_id': model_id, 'year': year});
            }
            else{
                return $http.post(URLS.USER_CAR, {'car_model_id': model_id});
            }
        };
        model.get_available_slots=function (model_id,type,city) {

            return fetch_from_api(URLS.BOOKING_ENDPOINT+"get_slots/?car_model="+model_id+"&type="+type+"&city="+city);
        };
        model.add_booking_address=function(booking_address){

            return $http.post(URLS.BOOKING_ADDRESS,booking_address);
        };
        model.userAddresses=function () {
            return fetch_from_api(URLS.USER_ADDRESS);
        };
        model.update_user_address =function(address_id,updated_address){
            return $http.patch(URLS.USER_ADDRESS+address_id+"/",updated_address);
        };
        model.update_booking_addresses = function (booking_id,updated_address) {

            return $http.patch(URLS.BOOKING_ADDRESS+booking_id+"/",updated_address);
        };
        model.saveAddress=function (address) {
            return $http.post(URLS.USER_ADDRESS,address);
        };
        model.makePayment=function (booking_id,payment_type) {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/initiate_payment/",payment_type);
        };
        model.citrus_pay=function (booking_id,payment_id,amount){
            return fetch_from_api(URLS.CITRUS_PAY+"?deviceType=web&bookingId="+booking_id+"&paymentId="+payment_id+"&amount="+amount);
        };
        model.get_booking_bill=function (booking_id){
            return fetch_from_api(URLS.BOOKING_BILL+booking_id);
        };
        model.getCurrentBooking=function(usercar,status){
            return fetch_from_api(URLS.BOOKING_ENDPOINT+"?usercar="+usercar+"&open_booking="+status+"&internal=True");
        };
        model.getUserCars=function(){
            return $http.get(URLS.USER_CAR).then(function(result){
                if(result.data) return result.data.results;
            });
        };
        model.getUserCarById = function (usercar) {
            return $http.get(URLS.USER_CAR+usercar);
        };
        model.loadPopularPackages= function(model){
            return fetch_from_api(URLS.POPULAR_PACKAGES+"&car_type="+model);
        };
        model.loadPackages=function (carModel,cityId) {
            return fetch_from_api(URLS.FETCH_PACKAGE+"car_model="+carModel+"&city="+cityId);
        };

        model.updateBooking=function (bookingId, data) {
            /*
             * This function will be used to update booking using patch request
             * If action update is required, then pass it in data.
             * */
            return $http.patch(URLS.BOOKING_ENDPOINT+bookingId+"/", data);
        };
        model.savePartnerDetails=function(partnerDetails){
            return $http.post(URLS.PARTNER_LEAD_ENDPOINT,partnerDetails);
        };
        model.loadReasons= function () {
            return $http.get(URLS.CANCELLATION_REASONS);
        };
        model.sendUserInquiry=function(Inquiry){
            return $http.post(URLS.USER_INQUIRY,Inquiry);
        };
        model.getLatestBooking = function(){
            return model.getUserCars().then(function(res){
                var latestUserCar = res;
                if(latestUserCar && latestUserCar.length>=1){
                    latestUserCar = latestUserCar[0];
                }
                return model.getCurrentBooking(latestUserCar.id, true).then(function (result) {
                    if(result.results.length>0){
                        //console.log("results",result);
                        return {'latestUserCar': latestUserCar, 'latestBooking':result.results[0]};
                    }else{
                        return null;
                    }
                });
            });
        };
        model.applyCoupon = function(bookingID,coupon){
            return $http.post(URLS.BOOKING_ENDPOINT+bookingID+"/add_coupon/",coupon);
        };
        model.deleteCoupon =function (couponId) {
            return $http.delete(URLS.DELETE_COUPON+couponId);
        };
        model.getUserBookings = function () {
            return $http.get(URLS.BOOKING_ENDPOINT+"get_booking_list/?open_booking=True");
        };
        model.bookingById = function (id) {
            return $http.get(URLS.BOOKING_ENDPOINT+id+"/"+"?internal=True");
        };
        model.bookingBill = function (bookingId) {
            return $http.get(URLS.PAYMENT_GATEWAY+bookingId+"/")
        };
        model.getPaymentDetails = function (token) {
            return $http.get(URLS.GET_BOOKING_FROM_TOKEN + "?token="+ token);
        };
        model.createChatInquiry = function (data) {
            return $http.post(URLS.INQUIRY_FROM_CHAT,data);
        };
        model.getCarInfoByID =function (id) {
            return $http.get(URLS.FETCH_CAR_MODEL+id);
        };
        model.postFeedback = function (data) {
            return $http.post(URLS.BOOKING_FEEDBACK, data);
        };
        model.getModelByYear = function (id,year) {
            return $http.get(URLS.FETCH_CAR_MODEL+id+"/model-by-year/?year="+year);
        };
        model.getBookingChecklist = function(bookingId,category){
            return $http.get(URLS.BOOKING_CHECKLIST+"?booking="+bookingId+"&category="+category+"&status=8&latest=true&ops_status__isnull=true");
        };
         model.getInteriorPhoto = function(bookingId,category){
            return $http.get(URLS.BOOKING_CHECKLIST+"?booking="+bookingId+"&category="+category);
        };
        model.getReferralCode = function(){
            return $http.get(URLS.REFERRAL_CODE);
        };
        model.getJobCards = function(bookingId){
            return $http.get(URLS.JOBCARD_ENDPOINT+"?booking="+bookingId+"&status=8&latest=true&ops_status__isnull=true")
        };
        model.getPanelList =function () {
            return $http.get(URLS.PANEL_LIST);
        };
    });