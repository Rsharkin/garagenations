    # SMS Templates
SMS_TEMPLATE_NEW_AUTH_CODE = 'NEW_AUTH_CODE'
SMS_TEMPLATE_APP_DOWNLOAD_LINK = 'APP_DOWNLOAD_LINK'
SMS_TEMPLATE_NEW_BOOKING = 'NEW_BOOKING'  # Sent from hooks and not here.
SMS_TEMPLATE_PAYMENT_SUCCESS = 'PAYMENT_SUCCESS'
SMS_TEMPLATE_PAYMENT_FAILURE = 'PAYMENT_FAILURE'
SMS_TEMPLATE_CAR_DELIVERED= 'CAR_DELIVERED'
SMS_TEMPLATE_NEW_LEAD = 'NEW_LEAD'
SMS_TEMPLATE_CASHBACK_PROMO = 'CASHBACK_PROMO'
SMS_TEMPLATE_RESET_PASSWORD = 'RESET_PASSOWRD'
SMS_TEMPLATE_PAYMENT_SUCCESS_OPS = 'PAYMENT_SUCCESS_OPS'


SMS_TEMPLATE_CHOICES = (
    (SMS_TEMPLATE_NEW_AUTH_CODE, 'NEW_AUTH_CODE'),
    (SMS_TEMPLATE_APP_DOWNLOAD_LINK, 'APP_DOWNLOAD_LINK'),
    (SMS_TEMPLATE_NEW_BOOKING, 'NEW_BOOKING'),
    (SMS_TEMPLATE_PAYMENT_SUCCESS, 'PAYMENT_SUCCESS'),
    (SMS_TEMPLATE_PAYMENT_FAILURE, 'PAYMENT_FAILURE'),
    (SMS_TEMPLATE_CAR_DELIVERED, 'CAR_DELIVERED'),
    (SMS_TEMPLATE_NEW_LEAD, 'NEW_LEAD'),
    (SMS_TEMPLATE_RESET_PASSWORD, SMS_TEMPLATE_RESET_PASSWORD),
)

SMS_TEMPLATES = {
    SMS_TEMPLATE_NEW_AUTH_CODE: '%(auth_code)s is your OTP to verify phone number in Bumper.',
    # SMS_TEMPLATE_NEW_AUTH_CODE: '%(auth_code)s is your verification code for Bumper.',
    SMS_TEMPLATE_APP_DOWNLOAD_LINK: "Dear Registered Customer, please download, for android click %(android_app_link)s and in case of iPhone click %(ios_app_link)s",
    SMS_TEMPLATE_NEW_BOOKING: 'Thank you for booking with Bumper. Your booking id is %(booking_id)s. You will hear from us shortly.',
    SMS_TEMPLATE_PAYMENT_SUCCESS: 'Your payment (id - %(booking_id)s) of Rs %(payment_amt)s for Bumper is successful.',
    SMS_TEMPLATE_PAYMENT_FAILURE: "Sorry, your payment (id - %(booking_id)s) of Rs %(payment_amt)s for Bumper couldn't go through. Please try again.",
    SMS_TEMPLATE_CAR_DELIVERED: "Your car has been delivered. Drive on! Call Bumper support(+91-%(support_num)s) if you face any issue.",
    SMS_TEMPLATE_NEW_LEAD: "Bump! There you are. Thanks for writing to Bumper. Our team will revert back soon with response to your query. Explore more features and offers on our android app. Download from here %(app_download_link)s",
    SMS_TEMPLATE_CASHBACK_PROMO: "You have %(cashback_amt)s credits in your bumper account. Use them to avail any of our services- car service, body repair or car wash.",
    SMS_TEMPLATE_RESET_PASSWORD: "Use %(new_password)s as password code for Bumper dashboard.",
    SMS_TEMPLATE_PAYMENT_SUCCESS_OPS: "Rs. %(amt_paid)s paid for booking %(booking_id)s, Payable %(payable)s. Payment status: %(payment_status)s, type: %(payment_type)s, mode: %(payment_mode)s.",
}

PUSH_TYPE_PAYMENT_RECEIVED = 'PAYMENT_RECEIVED'
PUSH_TYPES = (
    (PUSH_TYPE_PAYMENT_RECEIVED, 'PAYMENT_RECEIVED')
)
PUSH_TEMPLATES = {
    PUSH_TYPE_PAYMENT_RECEIVED: "Bill amount is successfully paid. We are bringing your car to your home. Ref Booking Id BUM%(booking_id)s.",
}

PUSH_TITLES = {
    PUSH_TYPE_PAYMENT_RECEIVED: "Payment Successful",
}

PUSH_TICKERS = {
    PUSH_TYPE_PAYMENT_RECEIVED: "Payment successful",
}

NOTICE_TYPE_APP = 'app'
NOTICE_TYPES = (
    (NOTICE_TYPE_APP, 'app'),
)

GROUP_BUMPER_USER = 'BumperUser'
GROUP_OPS_USER = 'OpsUser'
GROUP_OPS_ADMIN = 'OpsAdmin'
GROUP_WORKSHOP_USER = 'Driver'
GROUP_WORKSHOP_VAS_INCHARGE = 'VASIncharge'
GROUP_WORKSHOP_WORKSHOP_MANAGER = 'WorkshopManager'

DEVICE_TYPE_ANDROID = 'android'
DEVICE_TYPE_IOS = 'ios'
DEVICE_TYPE_WEB = 'web'

DEVICE_TYPES = (
    (DEVICE_TYPE_ANDROID, DEVICE_TYPE_ANDROID),
    (DEVICE_TYPE_IOS, DEVICE_TYPE_IOS),
    (DEVICE_TYPE_WEB, DEVICE_TYPE_WEB),
)

DURATION_ALL = 'all'
DURATION_TODAY = 'today'
DURATION_THIS_WEEK = 'this_week'
DURATION_LAST_WEEK = 'last_week'
DURATION_THIS_MONTH = 'this_month'
DURATION_LAST_MONTH = 'last_month'
DURATION_RANGE= 'range'

DURATION_TYPES = (
    (DURATION_ALL, 'All'),
    (DURATION_TODAY, 'Today'),
    (DURATION_THIS_WEEK, 'This Week'),
    (DURATION_LAST_WEEK, 'Last Week'),
    (DURATION_THIS_MONTH, 'This Month'),
    (DURATION_LAST_MONTH, 'Last Month'),
    (DURATION_RANGE, 'Date Range'),
)

import datetime
YEAR_CHOICES = []
for r in range(1925, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))


RESPONSE_STATUS_SUCCESS = 'success'
RESPONSE_STATUS_FAIL = 'fail'
RESPONSE_STATUS_ERROR = 'error'

GENERAL_ERROR_MESSAGE = 'There is some error on server. Please report it.'
FORM_ERROR_MESSAGE = 'Please fill all required fields correctly.'
ERROR_ONLY_POST_ALLOWED = 'Only POST requests are allowed on this URL.'
ERROR_INVALID_FILE_TYPE = 'For security reasons, this file type is not allowed to upload on our servers.'
ERROR_INVALID_FILE_SIZE = 'File size cannot be greater than 2 MB.'
ERROR_UPLOAD_FAILED = 'Failed to upload file.'


ACTION_ADDED_TO_CART = 1
ACTION_ADDED_TO_CART_WITHOUT_NOTIFICATION = 151
ACTION_ADDED_TO_CART_FOLLOWING_UP = 109
ACTION_BOOKING_CREATED = 2
ACTION_PICKUP_SCHEDULED = 3
ACTION_PICKUP_SCHEDULED_WITHOUT_NOTIFICATION = 152
ACTION_PICKUP_SCHEDULED_DRIVER_ASSIGNED = 101
ACTION_PICKUP_SCHEDULED_TEAM_ASSIGNED = 102
ACTION_PICKUP_SCHEDULED_DRIVER_READY_TO_GO = 103
ACTION_PICKUP_SCHEDULED_TEAM_READY_TO_GO = 104
ACTION_PICKUP_SCHEDULED_FOLLOWING_UP = 108
ACTION_PICKUP_SCHEDULED_CONFIRMED = 124

ACTION_SCHEDULED = 26
ACTION_SCHEDULED_WITHOUT_NOTIFICATION = 153
ACTION_DOORSTEP_SCHEDULED_FOLLOWING_UP = 111

ACTION_PICKUP_DRIVER_STARTED = 4
ACTION_TASK_TEAM_STARTED = 5
ACTION_DRIVER_AT_PICKUP_PLACE = 6
ACTION_DRIVER_CREATING_JOB_CARD = 107


ACTION_TASK_TEAM_AT_TASK_LOCATION = 7
ACTION_DRIVER_JOB_CARD_CREATED = 8
ACTION_CAR_PICKED_UP = 9
ACTION_CAR_REACHED_WORKSHOP = 10
ACTION_CAR_REACHED_WORKSHOP_CAR_RECEIVED_AT_WORKSHOP = 105
ACTION_CAR_REACHED_WORKSHOP_INSPECTION_SHEET_UPLOADED = 128
ACTION_CAR_REACHED_WORKSHOP_HANDOVER_SHEET_UPLOADED = 134
ACTION_CAR_REACHED_WORKSHOP_PENDING_PART_PROCUREMENT = 129
ACTION_CAR_REACHED_WORKSHOP_PENDING_CUSTOMER_APPROVAL = 130
ACTION_CAR_REACHED_WORKSHOP_PART_ARRIVED = 131
ACTION_CAR_REACHED_WORKSHOP_PART_PRICE_UPDATED = 135
ACTION_CAR_REACHED_WORKSHOP_PENDING_INSURANCE = 148
ACTION_CAR_REACHED_WORKSHOP_CUSTOMER_ACCEPTED_APPROVAL = 132
ACTION_CAR_REACHED_WORKSHOP_PENDING_WORKSHOP_ETA_CAR_JOB_SCHEDULE = 133
ACTION_CAR_REACHED_WORKSHOP_PENDING_CUSTOMER_ETA = 146

ACTION_CAR_JOB_SCHEDULED = 12

ACTION_WORK_IN_PROGRESS = 13
ACTION_REWORK_START_WORK_IN_PROGRESS = 145
ACTION_WIP_PAINT_STRIPPING = 112
ACTION_WIP_DENTING_UNDER_PROCESS = 113
ACTION_WIP_DENTING_REMOVAL_COMPLETED = 114
ACTION_WIP_BODY_FILLER_APPLICATION = 115
ACTION_WIP_BODY_FILLER_SANDING_DONE = 136
ACTION_WIP_PUTTY_APPLICATION = 116
ACTION_WIP_PUTTY_SANDING_DONE = 137
ACTION_WIP_PRIMER_MASKING = 138
ACTION_WIP_PRIMER_APPLICATION = 117
ACTION_WIP_PRIMER_SANDING_DONE = 139
ACTION_WIP_PAINT_MASKING = 140
ACTION_WIP_PAINTING_PROCESS = 118
ACTION_WIP_PAINT_DRYING = 119
ACTION_WIP_PAINT_DRIED = 141
ACTION_WIP_DULL_POLISHING = 121
ACTION_WIP_PARTS_FITTING = 142
ACTION_WIP_WAX_POLISHING = 120
ACTION_WIP_WASHING_DONE = 157
ACTION_WIP_VAS_DONE = 122
ACTION_WIP_READY_FOR_DELIVERY = 123
ACTION_WIP_WORK_COMPLETED_IN_WORKSHOP = 125
ACTION_WIP_QUALITY_CHECK_DONE_WORKSHOP_EXECUTIVE = 126

ACTION_QUALITY_CHECK_IN_PROGRESS = 14
ACTION_WORK_COMPLETED = 15
ACTION_PENDING_PAYMENT = 16
ACTION_PENDING_PAYMENT_VAS = 216  #This has same status changes as pending payment but different action for notification.
ACTION_PAYMENT_RECEIVED = 17
ACTION_DROP_SCHEDULE_PENDING = 18
ACTION_RETURN_WO_WORK_DROP_SCHEDULE_PENDING = 147
ACTION_DROP_SCHEDULED = 19

ACTION_DROP_SCHEDULED_DRIVER_READY_TO_GO = 106
ACTION_DROP_SCHEDULED_DRIVER_READY_TO_GO_QC_FAILED = 155
ACTION_DROP_SCHEDULED_DRIVER_FAILED_QC = 156

ACTION_DROP_CAR_ON_THE_WAY = 20
ACTION_CAR_REACHED_DROP_LOCATION = 21
ACTION_CAR_RETURNED_BY_CUSTOMER = 143
ACTION_RETURN_STARTED_FROM_CUSTOMER_LOC = 144
ACTION_CAR_DELIVERED = 22
ACTION_BOOKING_CLOSED = 23
ACTION_BOOKING_CLOSED_FEEDBACK_RECEIVED = 154
ACTION_BOOKING_CANCELLED = 24
ACTION_BOOKING_CANCELLED_LOST = 127
ACTION_CAR_DELIVERY_CONFIRMED = 25


# Do not allow to set these status from OPS panel or Through APP. These are used only while internal processing in
# ops flow.
# Notifications and hooks will be mapped to these status for easy processing.
# used mainly in process_hooks function in general Manager.
# This action will not change any status, as we do not know which status booking is in.
ACTION_BOOKING_CHANGED = 51
ACTION_BOOKING_USER_PAYMENT_SUCCESS = 52
ACTION_BOOKING_REQUEST_FEEDBACK = 53
ACTION_BOOKING_REQUEST_RATE_US = 54
ACTION_BOOKING_REQUEST_FILL_PROFILE = 55
ACTION_BOOKING_REQUEST_FILL_CAR_INFO = 56
ACTION_BOOKING_QUICK_PICKUP = 57
ACTION_BOOKING_BOOKING_ESCALATION = 58
ACTION_NOTIFY_CUSTOMER_CONCERN = 59
ACTION_BOOKING_NO_CHANGE = 60


ACTION_DICT = {
    ACTION_ADDED_TO_CART: {'status': 1, 'ops_status': None},
    ACTION_ADDED_TO_CART_WITHOUT_NOTIFICATION: {'status': 1, 'ops_status': None},
    ACTION_ADDED_TO_CART_FOLLOWING_UP: {'status': 1, 'ops_status': 8},
    ACTION_BOOKING_CREATED: {'status': 2, 'ops_status': None},
    ACTION_PICKUP_SCHEDULED: {'status': 3, 'ops_status': None},
    ACTION_PICKUP_SCHEDULED_WITHOUT_NOTIFICATION: {'status': 3, 'ops_status': None},
    ACTION_SCHEDULED: {'status': 26, 'ops_status': None},
    ACTION_SCHEDULED_WITHOUT_NOTIFICATION: {'status': 26, 'ops_status': None},
    ACTION_PICKUP_SCHEDULED_CONFIRMED: {'status': 3, 'ops_status': 25},
    ACTION_PICKUP_SCHEDULED_DRIVER_ASSIGNED: {'status': 3, 'ops_status': 1},
    ACTION_PICKUP_SCHEDULED_TEAM_ASSIGNED: {'status': 26, 'ops_status': 2},
    ACTION_PICKUP_SCHEDULED_DRIVER_READY_TO_GO: {'status': 3, 'ops_status': 3},
    ACTION_PICKUP_SCHEDULED_TEAM_READY_TO_GO: {'status': 26, 'ops_status': 4},
    ACTION_PICKUP_SCHEDULED_FOLLOWING_UP: {'status': 3, 'ops_status': 8},
    ACTION_DOORSTEP_SCHEDULED_FOLLOWING_UP: {'status': 26, 'ops_status': 8},

    ACTION_PICKUP_DRIVER_STARTED: {'status': 4, 'ops_status': None},
    ACTION_DRIVER_AT_PICKUP_PLACE: {'status': 6, 'ops_status': None},
    ACTION_DRIVER_CREATING_JOB_CARD: {'status': 6, 'ops_status': 5},

    ACTION_DRIVER_JOB_CARD_CREATED: {'status': 8, 'ops_status': None},
    ACTION_CAR_PICKED_UP: {'status': 9, 'ops_status': None},
    ACTION_CAR_REACHED_WORKSHOP: {'status': 10, 'ops_status': None},
    ACTION_CAR_REACHED_WORKSHOP_CAR_RECEIVED_AT_WORKSHOP: {'status': 10, 'ops_status': 6},
    ACTION_CAR_REACHED_WORKSHOP_INSPECTION_SHEET_UPLOADED: {'status': 10, 'ops_status': 9},
    ACTION_CAR_REACHED_WORKSHOP_HANDOVER_SHEET_UPLOADED: {'status': 10, 'ops_status': 31},
    ACTION_CAR_REACHED_WORKSHOP_PENDING_PART_PROCUREMENT: {'status': 10, 'ops_status': 32},
    ACTION_CAR_REACHED_WORKSHOP_PENDING_INSURANCE: {'status': 10, 'ops_status': 45},
    ACTION_CAR_REACHED_WORKSHOP_PENDING_CUSTOMER_APPROVAL: {'status': 10, 'ops_status': 33},
    ACTION_CAR_REACHED_WORKSHOP_PART_ARRIVED: {'status': 10, 'ops_status': 34},
    ACTION_CAR_REACHED_WORKSHOP_PART_PRICE_UPDATED: {'status': 10, 'ops_status': 36},
    ACTION_CAR_REACHED_WORKSHOP_CUSTOMER_ACCEPTED_APPROVAL: {'status': 10, 'ops_status': 35},
    ACTION_CAR_REACHED_WORKSHOP_PENDING_WORKSHOP_ETA_CAR_JOB_SCHEDULE: {'status': 10, 'ops_status': 29},
    ACTION_CAR_REACHED_WORKSHOP_PENDING_CUSTOMER_ETA: {'status': 10, 'ops_status': 46},

    ACTION_CAR_JOB_SCHEDULED: {'status': 12, 'ops_status': None},

    ACTION_WORK_IN_PROGRESS: {'status': 13, 'ops_status': None},
    ACTION_REWORK_START_WORK_IN_PROGRESS: {'status': 13, 'ops_status': None},
    ACTION_WIP_PAINT_STRIPPING: {'status': 13, 'ops_status': 13},
    ACTION_WIP_DENTING_UNDER_PROCESS: {'status': 13, 'ops_status': 14},
    ACTION_WIP_DENTING_REMOVAL_COMPLETED: {'status': 13, 'ops_status': 15},
    ACTION_WIP_BODY_FILLER_APPLICATION: {'status': 13, 'ops_status': 16},
    ACTION_WIP_BODY_FILLER_SANDING_DONE: {'status': 13, 'ops_status': 37},
    ACTION_WIP_PUTTY_APPLICATION: {'status': 13, 'ops_status': 17},
    ACTION_WIP_PUTTY_SANDING_DONE: {'status': 13, 'ops_status': 38},
    ACTION_WIP_PRIMER_MASKING: {'status': 13, 'ops_status': 39},
    ACTION_WIP_PRIMER_APPLICATION: {'status': 13, 'ops_status': 18},
    ACTION_WIP_PRIMER_SANDING_DONE: {'status': 13, 'ops_status': 40},
    ACTION_WIP_PAINT_MASKING: {'status': 13, 'ops_status': 41},
    ACTION_WIP_PAINTING_PROCESS: {'status': 13, 'ops_status': 19},
    ACTION_WIP_PAINT_DRYING: {'status': 13, 'ops_status': 20},
    ACTION_WIP_PAINT_DRIED: {'status': 13, 'ops_status': 42},
    ACTION_WIP_DULL_POLISHING: {'status': 13, 'ops_status': 22},
    ACTION_WIP_PARTS_FITTING: {'status': 13, 'ops_status': 43},
    ACTION_WIP_WAX_POLISHING: {'status': 13, 'ops_status': 21},
    ACTION_WIP_WASHING_DONE: {'status': 13, 'ops_status': 49},
    ACTION_WIP_VAS_DONE: {'status': 13, 'ops_status': 23},
    ACTION_WIP_READY_FOR_DELIVERY: {'status': 13, 'ops_status': 24},
    ACTION_WIP_WORK_COMPLETED_IN_WORKSHOP: {'status': 13, 'ops_status': 26},
    ACTION_WIP_QUALITY_CHECK_DONE_WORKSHOP_EXECUTIVE: {'status': 13, 'ops_status': 27},

    ACTION_QUALITY_CHECK_IN_PROGRESS: {'status': 14, 'ops_status': None},
    ACTION_WORK_COMPLETED: {'status': 15, 'ops_status': None},
    ACTION_PENDING_PAYMENT: {'status': 16, 'ops_status': None},
    ACTION_PENDING_PAYMENT_VAS: {'status': 16, 'ops_status': None},
    ACTION_DROP_CAR_ON_THE_WAY: {'status': 20, 'ops_status': None},
    ACTION_CAR_REACHED_DROP_LOCATION: {'status': 21, 'ops_status': None},
    ACTION_CAR_RETURNED_BY_CUSTOMER: {'status': 27, 'ops_status': None},
    ACTION_RETURN_STARTED_FROM_CUSTOMER_LOC: {'status': 27, 'ops_status': 44},

    ACTION_PAYMENT_RECEIVED: {'status': 17, 'ops_status': None},
    ACTION_DROP_SCHEDULE_PENDING: {'status': 18, 'ops_status': None},
    ACTION_RETURN_WO_WORK_DROP_SCHEDULE_PENDING: {'status': 18, 'ops_status': None},
    ACTION_TASK_TEAM_STARTED: {'status': 5, 'ops_status': None},
    ACTION_TASK_TEAM_AT_TASK_LOCATION: {'status': 7, 'ops_status': None},
    ACTION_DROP_SCHEDULED: {'status': 19, 'ops_status': None},

    ACTION_DROP_SCHEDULED_DRIVER_READY_TO_GO: {'status': 19, 'ops_status': 3},
    ACTION_DROP_SCHEDULED_DRIVER_READY_TO_GO_QC_FAILED: {'status': 19, 'ops_status': 48},
    ACTION_DROP_SCHEDULED_DRIVER_FAILED_QC: {'status': 19, 'ops_status': 47},

    ACTION_CAR_DELIVERED: {'status': 22, 'ops_status': None},
    ACTION_CAR_DELIVERY_CONFIRMED: {'status': 25, 'ops_status': None},

    ACTION_BOOKING_CANCELLED: {'status': 24, 'ops_status': None},
    ACTION_BOOKING_CANCELLED_LOST: {'status': 24, 'ops_status': 28},
    ACTION_BOOKING_CLOSED: {'status': 23, 'ops_status': None},
    ACTION_BOOKING_CLOSED_FEEDBACK_RECEIVED: {'status': 23, 'ops_status': 30},

    ACTION_BOOKING_CHANGED: {'status': None, 'ops_status': None},
    ACTION_BOOKING_USER_PAYMENT_SUCCESS: {'status': None, 'ops_status': None},
    ACTION_BOOKING_REQUEST_FEEDBACK: {'status': None, 'ops_status': None},
    ACTION_BOOKING_REQUEST_RATE_US: {'status': None, 'ops_status': None},
    ACTION_BOOKING_REQUEST_FILL_PROFILE: {'status': None, 'ops_status': None},
    ACTION_BOOKING_REQUEST_FILL_CAR_INFO: {'status': None, 'ops_status': None},
    ACTION_BOOKING_BOOKING_ESCALATION: {'status': None, 'ops_status': None},
    ACTION_NOTIFY_CUSTOMER_CONCERN: {'status': None, 'ops_status': None},
    ACTION_BOOKING_NO_CHANGE: {'status': None, 'ops_status': False},
}

VERIFICATION_EMAIL_TEMPLATE = 'Email Verification'

from decimal import Decimal
TWO_PLACES = Decimal("0.01")
SERVICE_TAX_FACTOR = Decimal('14')
VAT_FACTOR = Decimal('14.5')
KK_TAX_FACTOR = Decimal('0.5')
SB_TAX_FACTOR = Decimal('0.5')
CGST_FACTOR = Decimal('9')
SGST_FACTOR = Decimal('9')
IGST_FACTOR = Decimal('18')
