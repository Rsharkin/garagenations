/**
 * Created by Indy on 28/02/17.
 */
angular.module('ops.views.editBookingNotifications',[
    'ops.services.booking',
    'ops.services.common'
])
    .controller('EditBookingNotificationCtrl', function EditBookingNotificationCtrl($state, $scope, $uibModal,
                                                                                    BookingService, CommonService){
        var self = this;
        self.booking = BookingService.getCurrentBooking();
        self.messagesToUser = null;
        self.messagesForBooking = null;

        self.actionMapping = {
            '1': 'ADDED_TO_CART',
            '2': 'BOOKING_CREATED',
            '3': 'PICKUP_SCHEDULED',
            '101': 'PICKUP_SCHEDULED_DRIVER_ASSIGNED',
            '102': 'PICKUP_SCHEDULED_TEAM_ASSIGNED',
            '103': 'PICKUP_SCHEDULED_DRIVER_READY_TO_GO',
            '104': 'PICKUP_SCHEDULED_TEAM_READY_TO_GO',
            '4': 'PICKUP_DRIVER_STARTED',
            '5': 'TASK_TEAM_STARTED',
            '6': 'DRIVER_AT_PICKUP_PLACE',
            '107': 'DRIVER_CREATING_JOB_CARD',
            '7': 'TASK_TEAM_AT_TASK_LOCATION',
            '8': 'DRIVER_JOB_CARD_CREATED',
            '9': 'CAR_PICKED_UP',
            '10': 'CAR_REACHED_WORKSHOP',
            '105': 'CAR_RECEIVED_AT_WORKSHOP',
            '12': 'CAR_JOB_SCHEDULED',
            '13': 'WORK_IN_PROGRESS',
            '14': 'QUALITY_CHECK_IN_PROGRESS',
            '15': 'WORK_COMPLETED',
            '16': 'PENDING_PAYMENT',
            '17': 'PAYMENT_RECEIVED',
            '18': 'DROP_SCHEDULE_PENDING',
            '19': 'DROP_SCHEDULED',
            '106': 'DROP_SCHEDULED_DRIVER_READY_TO_GO',
            '20': 'DROP_CAR_ON_THE_WAY',
            '21': 'CAR_REACHED_DROP_LOCATION',
            '22': 'CAR_DELIVERED',
            '23': 'BOOKING_CLOSED',
            '24': 'BOOKING_CANCELLED',
            '25': 'CAR_DELIVERY_CONFIRMED',
            '51': 'BOOKING_CHANGED',
        };


        function getMessagesSentForBooking(){
            var filters = [];
            filters.push({ 'op': 'eq', 'field': 'booking_id', 'data': self.booking.id });
            CommonService.getReportData('report_booking_notifications_sent', filters)
                .then(function (data) {
                    self.messagesForBooking = data.rows;

                });

            filters = [];
            filters.push({ 'op': 'eq', 'field': 'user_id', 'data': self.booking.user });
            CommonService.getReportData('report_booking_notifications_sent', filters)
                .then(function (data) {
                    self.messagesToUser = data.rows;

                });
        }
        getMessagesSentForBooking();

        function openEmailPopup(template){
            var modalInstance = $uibModal.open({
                template: template
            });
        }
        self.openEmailPopup = openEmailPopup;
    });