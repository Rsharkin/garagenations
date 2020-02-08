angular.module('ops.services.booking',[
])
    .service('BookingService', function($http, $q){
        var model = this,
            URLS={
                BOOKING_ENDPOINT: '/api/booking/',
                BOOKING_STATUS_ENDPOINT: '/api/booking-status/',
                BOOKING_FOLLOWUP_ENDPOINT: '/api/booking-followup/',
                PACKAGE_ENDPOINT: '/api/package/',
                PANEL_PRICE_ENDPOINT: '/api/panel-price/',
                BOOKING_PACKAGE_ENDPOINT: '/api/booking-package/',
                DENTING_PANEL_ENDPOINT: '/api/booking-panel/',
                BOOKING_BILL:'/api/v2/booking-bill/',
                GET_NOTIFICATION_DETAILS: '/core/send-notification/',
                BOOKING_ADDRESS:'/api/booking-address/',
                FETCH_CAR_MODEL:'/api/model/?format=json&limit=0',
                USER_CAR:'/api/usercar/',
                PAYMENT_ENDPOINT:'/api/payment/',
                DISCOUNT_ENDPOINT:'/api/booking-discount/',
                NOTIFICATION_ENDPOINT:'/api/notification/',
                JOBCARD_ENDPOINT:'/api/booking-jobcard/',
                BOOKING_FEEDBACK_ENDPOINT:'/api/booking-feedback/',
                BOOKING_CUSTOMER_FEEDBACK_ENDPOINT:'/api/booking-cust-feedback/',
                PROFORMA_INVOICE_ENDPOINT:'/api/booking-proforma-invoice/',
                BOOKING_REWORK_PANEL:'/api/booking-rework-panel/',
                QUALITY_CHECK_ENDPOINT:'/api/booking-quality-checks/',
                CHECKLIST_ENDPOINT:'/api/booking-checklist/',
                PANEL_LIST:'/api/panel/?part_type=1&internal=false',
                BOOKING_REWORK_PACKAGE:'/api/booking-rework-package/',
                BOOKING_FLAG_ENDPOINT:'/api/booking-flag/',
                PURCHASE_REQUISTION_TERM: '/api/part-doc/',
                PART_QUOTE_ENDPOINT: '/api/part-quote/',
                PART_VENDOR_ENDPOINT: '/api/part-vendor/',
                EXPECTED_EOD_ENDPOINT: '/api/expected-eod/'
            },
            currentBooking = null // Used as shared data between edit booking controllers.
        ;

        model.setCurrentBooking = function(booking){
            model.currentBooking = booking;
        };
        model.updateTypeOfWork = function (bookingPanel, typeId,internalPanelPrice) {
            var data ={
                'panel':typeId
            };
            if(internalPanelPrice && (internalPanelPrice.part_price || internalPanelPrice.material_price || internalPanelPrice.labour_price)){
                data.part_price = internalPanelPrice.part_price;
                data.material_price = internalPanelPrice.material_price;
                data.labour_price = internalPanelPrice.labour_price;
            }
            return $http.patch(URLS.DENTING_PANEL_ENDPOINT+bookingPanel+"/",data);
        };
        model.getCurrentBooking = function(){
            return model.currentBooking;
        };

        model.clearCurrentBooking = function(){
            model.currentBooking = null;
        };

        model.getBookingById = function(bookingId){
            return $http.get(URLS.BOOKING_ENDPOINT + bookingId + "/"+'?internal=True').then(function(result){
                return result.data;
            });
        };

        model.saveBooking = function(bookingId, data, action_statusToSet){
            if(action_statusToSet){
                data.action = action_statusToSet;
            }
            return $http.patch(URLS.BOOKING_ENDPOINT + bookingId + "/", data);
        };

        model.getBookingFollowups = function(bookingId){
            return $http.get(URLS.BOOKING_ENDPOINT + bookingId + "/followup/?follow_for=2").then(function(result){
                if(result.data) return result.data.followup;
            });
        };

        model.saveBookingFollowups = function(bookingId, data){
            return $http.patch(URLS.BOOKING_ENDPOINT + bookingId + "/followup/", data);
        };

        model.getWorkshopNotes = function(bookingId){
            return $http.get(URLS.BOOKING_ENDPOINT + bookingId + "/followup/").then(function(result){
                if(result.data) return result.data.followup;
            });
        };

        model.saveWorkshopNotes = function(bookingId, data){
            return $http.patch(URLS.BOOKING_ENDPOINT + bookingId + "/followup/", data);
        };

        model.getPackages = function(usercar_id, bookingCity){
            return $http.get(URLS.PACKAGE_ENDPOINT+"?usercar_id="+usercar_id+'&internal=True&city='+bookingCity).then(function(result){
                return result.data.results;
            });
        };

        model.addPackageToBooking = function(bookingId, packageId, manualPrice, isExtra){
            var data = {
                'booking': bookingId,
                'package_id': packageId,
                'extra': false
            };
            if(isExtra){
                data.extra = true;
            }
            if(manualPrice && (manualPrice.part_price || manualPrice.material_price || manualPrice.labour_price )){
                data.part_price = manualPrice.part_price;
                data.material_price = manualPrice.material_price;
                data.labour_price = manualPrice.labour_price;
            }
            return $http.post(URLS.BOOKING_PACKAGE_ENDPOINT, data);
        };

        model.removePackageFromBooking = function(bookingPackageId){
            return $http.delete(URLS.BOOKING_PACKAGE_ENDPOINT+bookingPackageId+"/").then(function(response){
                if(response.status == 204){
                    return 'removed';
                }
            });
        };

        // model.getPanelsByCarModel = function(carModelId){
        //     return $http.get(URLS.PANEL_PRICE_ENDPOINT+"?carmodel_id="+carModelId+'&internal=True&part_type=1,2').then(function(result){
        //         if(result.data) return result.data.results;
        //     });
        // };

        model.getPanelsByUserCarId = function(userCarId, fullBody, bookingCity){
            var arg =null;
            if(fullBody){
                arg = 'fbb=True';
            }
            else{
                arg = 'fbb=false';
            }
            return $http.get(URLS.PANEL_PRICE_ENDPOINT+"?usercar="+userCarId+'&'+arg+'&city='+ bookingCity+'&internal=True&part_type=1,2').then(function(result){
                if(result.data) return result.data.results;
            });
        };

        model.addPanelToPackage = function(bookingPackageId, panelId, internalPanelPrice, isExtra){
            var data = {
                'booking_package': bookingPackageId,
                'panel': panelId,
                'extra': false
            };
            if(isExtra){
                data.extra = true;
            }
            if(internalPanelPrice && (internalPanelPrice.part_price || internalPanelPrice.material_price || internalPanelPrice.labour_price)){
                data.part_price = internalPanelPrice.part_price;
                data.material_price = internalPanelPrice.material_price;
                data.labour_price = internalPanelPrice.labour_price;
            }
            return $http.post(URLS.DENTING_PANEL_ENDPOINT, data);
        };

        model.addReworkPanelToBooking = function(data){
            return $http.post(URLS.BOOKING_REWORK_PANEL, data);
        };

        model.removeReworkPanelFromBooking = function(rework_panel_id){
            return $http.delete(URLS.BOOKING_REWORK_PANEL + rework_panel_id + "/").then(function(response){
                if(response.status == 204){
                    return 'removed';
                }
            });
        };

        model.addReworkPackageToBooking = function(data){
            return $http.post(URLS.BOOKING_REWORK_PACKAGE, data);
        };

        model.removeReworkPackageFromBooking = function(rework_package_id){
            return $http.delete(URLS.BOOKING_REWORK_PACKAGE + rework_package_id + "/").then(function(response){
                if(response.status == 204){
                    return 'removed';
                }
            });
        };

        model.getReworkOnBooking = function(bookingId){
            return $http.get(URLS.BOOKING_ENDPOINT+bookingId+'/rework_details/').then(function(result){
                if(result.data) return result.data;
            });
        };

        model.updatePanelToPackage = function(bookingPackageId, panelId, internalPanelPrice, extra){
            var data = {
                'part_price': internalPanelPrice.part_price,
                'material_price': internalPanelPrice.material_price,
                'labour_price': internalPanelPrice.labour_price
            };
            if(extra){
                data.extra= extra;
            }
            return $http.patch(URLS.DENTING_PANEL_ENDPOINT+panelId+"/", data);
        };

        model.removePanelFromPackage = function(bookingPanelId){
            return $http.delete(URLS.DENTING_PANEL_ENDPOINT+bookingPanelId+"/").then(function(response){
                if(response.status == 204){
                    return 'removed';
                }
            });
        };

        model.getBookingStatuses = function(){
            return $http.get(URLS.BOOKING_STATUS_ENDPOINT).then(function(response){
                if(response.data) return response.data.results;
            });
        };

        model.getBookingBill =function (booking_id)
        {
            return $http.get(URLS.BOOKING_BILL+booking_id+"/");
        };

        model.updateBookingAddress=function (updates) {
            return $http.post(URLS.BOOKING_ADDRESS, updates);

        };

        model.getModel = function(brand_name){
            if(brand_name){
                return $http.get(URLS.FETCH_CAR_MODEL+"&search="+brand_name);
            }else{
                return $http.get(URLS.FETCH_CAR_MODEL+"&popular=True");
            }
        };

        model.saveUserCar =function (userId,modelId,year) {
            if(year){
                return $http.post(URLS.USER_CAR,{'car_model_id':modelId,'user_id':userId,'year':year});
            }
            else{
                return $http.post(URLS.USER_CAR,{'car_model_id':modelId,'user_id':userId});
            }
        };

        model.createBooking =function(data){
            return $http.post(URLS.BOOKING_ENDPOINT,data);
        };

        model.checkCoupon = function(bookingId, coupon_code){
            return $http.get(URLS.BOOKING_ENDPOINT + bookingId + "/get_coupon_details/?coupon_code="+coupon_code);
        };

        model.applyCoupon = function(bookingId, coupon_code){
            return $http.post(URLS.BOOKING_ENDPOINT + bookingId + "/add_coupon/",{
                'coupon_code': coupon_code
            });
        };

        model.applyCashDiscount = function(bookingId, discountAmounts, discountReason, discountReasonDD){
            return $http.post(URLS.DISCOUNT_ENDPOINT,{
                'booking': bookingId,
                'labour_discount': discountAmounts.labour_discount,
                'material_discount': discountAmounts.material_discount,
                'part_discount': discountAmounts.part_discount,
                'reason': discountReason,
                'reason_dd': discountReasonDD
            });
        };

        model.getAppliedCashDiscounts = function(bookingId){
            return $http.get(URLS.DISCOUNT_ENDPOINT + "?booking=" + bookingId);
        };

        model.generateInvoice = function(booking_id)
        {
            return $http.patch(URLS.BOOKING_ENDPOINT+booking_id+"/save_invoice/");
        };

        model.generateProformaInvoice = function(data)
        {
            return $http.post(URLS.PROFORMA_INVOICE_ENDPOINT, data);
        };

        model.cancelProformaInvoice = function(invoiceId)
        {
            return $http.patch(URLS.PROFORMA_INVOICE_ENDPOINT+invoiceId+"/", {"status": "2"});
        };

        model.initiatePayment = function(booking_id,payment_type)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/initiate_payment/",payment_type);
        };

        model.initiateProformaPayment = function(booking_id, data)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/initiate_payment_proforma/",data);
        };

        model.generatePaymentLink = function(booking_id)
        {
            return $http.get(URLS.BOOKING_ENDPOINT+booking_id+"/generate_payment_token/");
        };

        model.getPaymentData =function(paymentId)
        {
            return $http.get(URLS.PAYMENT_ENDPOINT + paymentId + "/");
        };

        model.addPayment =function(data)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+ data.bookingId + "/make_payment/", data);
        };

        model.getPaymentsForBookingData =function(bookingId)
        {
            return $http.get(URLS.BOOKING_ENDPOINT+bookingId+"/get_payments/");
        };

        model.alertBookingChanged = function(booking_id)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/alert_booking_changed/");
        };

        model.sendEODMessage = function(booking_id, data)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/send_eod_notification/", data);
        };

        model.saveManualEODMessage = function(booking_id, data)
        {
            return $http.post(URLS.BOOKING_ENDPOINT+booking_id+"/save_manually_sent_eod_message/", data);
        };

        model.getEODMessage = function(booking_id, data)
        {
            return $http.get(URLS.BOOKING_ENDPOINT+booking_id+"/get_eod_notification/", data);
        };

        model.getJobCards =function(bookingId)
        {
            return $http.get(URLS.JOBCARD_ENDPOINT+"?booking="+bookingId);
        };

        model.createFeedback = function(data)
        {
            return $http.post(URLS.BOOKING_FEEDBACK_ENDPOINT, data);
        };

        model.updateFeedback = function(feedbackId, data)
        {
            return $http.patch(URLS.BOOKING_FEEDBACK_ENDPOINT+feedbackId+"/", data);
        };

        model.getFeedback = function(bookingId)
        {
            return $http.get(URLS.BOOKING_FEEDBACK_ENDPOINT+"?booking="+bookingId).then(function(result){
                if(result.data.results) return result.data.results[0];
            });
        };

        model.getCustomerFeedback = function(bookingId)
        {
            return $http.get(URLS.BOOKING_CUSTOMER_FEEDBACK_ENDPOINT+"?booking="+bookingId).then(function(result){
                return result.data.results;
            });
        };

        model.getQualityChecks = function (bookingId) {
            return $http.get(URLS.CHECKLIST_ENDPOINT+"?booking="+bookingId+"&is_qc=True").then(function(result){
                return result.data.results;
            });
        };

        model.getOldQualityChecks = function (bookingId) {
            return $http.get(URLS.QUALITY_CHECK_ENDPOINT+"?booking="+bookingId).then(function(result){
                return result.data.results;
            });
        };

        model.getBookingChecklist = function(bookingId, category){
            var additionalUrl = "?booking="+bookingId;
            if(category){
                additionalUrl += "&category="+category;
            }
            return $http.get(URLS.CHECKLIST_ENDPOINT + additionalUrl ).then(function(response){
                return response.data.results;
            });
        };

        model.getPanelList =function () {
            return $http.get(URLS.PANEL_LIST);
        };

        model.saveDeliveryReasonDesc = function(bookingId,data){
            return $http.patch(URLS.BOOKING_ENDPOINT+bookingId+"/",data);
        };

        model.addBookingFlag = function(data){
            return $http.post(URLS.BOOKING_FLAG_ENDPOINT, data);
        };

        model.removeBookingFlag = function(bookingFlagId){
            return $http.delete(URLS.BOOKING_FLAG_ENDPOINT+bookingFlagId+"/");
        };
        model.getModelByYear = function (id,year) {
            return $http.get('/api/model/'+id+"/model-by-year/?year="+year);
        };

        model.getPurchaseRequisitionTerm = function (id) {
            return $http.get(URLS.PURCHASE_REQUISTION_TERM+id+"/").then(function(response){
                return response.data;
            });
        };

        model.getPurchaseRequisitionTermByPartId = function (partId) {
            return $http.get(URLS.PURCHASE_REQUISTION_TERM+"?booking_part=" + partId).then(function(response){
                return response.data.results?response.data.results[0]:null;
            });
        };

        model.createPurchaseRequisitionTerm = function (data) {
            return $http.post(URLS.PURCHASE_REQUISTION_TERM, data);
        };

        model.updatePurchaseRequisitionTerm = function (id, data) {
            return $http.patch(URLS.PURCHASE_REQUISTION_TERM+id+"/", data).then(function(response){
                return response.data;
            });
        };

        model.getPartQuote = function (id) {
            return $http.get(URLS.PART_QUOTE_ENDPOINT+"?booking_part_doc="+id).then(function(response){
                return response.data.results;
            });
        };

        model.addPartQuote = function (data) {
            return $http.post(URLS.PART_QUOTE_ENDPOINT, data);
        };

        model.updatePartQuote = function (id, data) {
            return $http.patch(URLS.PART_QUOTE_ENDPOINT+id+"/", data);
        };

        model.deletePartQuote = function (id) {
            return $http.delete(URLS.PART_QUOTE_ENDPOINT+id+"/");
        };

        model.getPartVendors = function () {
            return $http.get(URLS.PART_VENDOR_ENDPOINT).then(function(response){
                return response.data.results;
            });
        };

        model.setExpectedEOD = function(data) {
            return $http.post(URLS.EXPECTED_EOD_ENDPOINT, data);
        };

        model.getExpectedEODList = function(bookingId) {
            return $http.get(URLS.EXPECTED_EOD_ENDPOINT + '?booking='+bookingId).then(function(response){
                return response.data.results;
            });
        };

    });