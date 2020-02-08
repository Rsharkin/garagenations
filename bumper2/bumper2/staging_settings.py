# -*- coding: utf-8 -*-

from bumper2.settings import *

DEBUG = False
BUMPER_ENV = 'STAGING'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bumper2',
        'USER': 'ninja',
        'PASSWORD': 'BumPer@(!!',
        'HOST': 'localhost',
    },
    'bumperv1': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bumper',
        'USER': 'ninja',
        'PASSWORD': 'BumPer@(!!',
        'HOST': 'localhost',
    },
}

PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": "AIzaSyDv045E6Z3sZ-915Kf5XqhvR4cWPYAz8kM",
    "APNS_CERTIFICATE": "/srv/www/bumper2/deployment/stagingDev.pem",
    "APNS_HOST": "gateway.sandbox.push.apple.com",
}

ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST = ['praveena@bumper.com', 'pravin.raj@bumper.com', 'deepakraj@bumper.com',
                                       'veeresh@bumper.com', 'rishi.sharma@bumper.com', 'anuj@bumper.com']


ALERT_SMS_PAYMENT_SUCCESSFUL = [
    '8800165656',  # Inderjeet
]
ALERT_QUICK_PICKUP = [
    '8800165656',  # Inderjeet
]
PAYMENT_URL = "https://staging.bumper.com/payment/?booking_id=%s&utm_source=payment"

SHOW_CHAT_OPTION = False
CHAT_OPTION_TO_SHOW = 'intercom'  # [intercom/ freshchat]

SMS_FAILURE_ALERT_LIST = ['inderjeet@autoninja.in', 'anuj@autoninja.in']

#CITRUS_MERCHANT_ACCESS_KEY = 'ATJP15ZY1GDG0VAAHQXX'
#CITRUS_MERCHANT_SECRET_KEY = 'e048d67c7541fd422cec0395e50169d1ed422e0f'
CITRUS_RETURN_URL = 'http://staging.bumper.com/payment/citrus-pay/'
CITRUS_WEBSITE_RETURN_URL = 'http://staging.bumper.com/payment/citrus-pay-web/'
#CITRUS_VANITY_URL = 'mvw7nadn8e'
#CITRUS_FORM_POST_URL = "https://sandbox.citruspay.com/%s" % CITRUS_VANITY_URL
RAZOR_PAY_API_KEY = 'rzp_test_IIfYoYxyK4woPx'
RAZOR_PAY_API_SECRET = '2sj3zvcG6QqhPmUNk1Bw4zRL'
TXNID_APPEND_TEXT = 'STAG'
PAYMENT_GATEWAY_TO_USE = 2 # 1-Citrus, 2-Razorpay
DIRECT_PAYMENT_URL_BASE ="https://staging.bumper.com/direct-payment/?pid=%s"
FEEDBACK_BASE_URL = 'https://staging.bumper.com/feedback/?token=%s'
BASE_URL = 'https://staging.bumper.com/'
BASE_URL_WEB = 'https://staging.bumper.com/'

PROCESS_IN_ASYNC = True

STATIC_FILES_VERSION = '1.3.26'
WEB_STATIC_FILES_VERSION = '1.2.32'

OPBEAT = {
    'ORGANIZATION_ID': '8e41e3be8eea4489b118bd9dff00188c',
    'APP_ID': '2679047dae',
    'SECRET_TOKEN': 'd4a2f6ce3eaed82aadc646c3d374c0f09286291d',
}
OPBEAT_WEBSITE = {
    'ORGANIZATION_ID': '8e41e3be8eea4489b118bd9dff00188c',
    'APP_ID': 'b199cf0a1b',
    'SECRET_TOKEN': 'd4a2f6ce3eaed82aadc646c3d374c0f09286291d',
}

LOCALYTICS_KEY = ""
GOOGLE_ANALYTICS_UNIVERSAL_KEY = ""

BILL_UPLOAD_CAMPAIGN = True
BOTO_S3_BUCKET_BOOKING = 'unbox-bumper2-staging-booking'

PAYTM_MERCHANT_KEY = 'QRl3088qH_wtuXuz'
PAYTM_MERCHANT_ID = '2086346e-dda3-48a6-8b27-b65036a0c707'
PAYTM_SALES_WALLET_GUID = "3e7027bf-3619-4d84-ae54-2219009f7ffa"
PAYTM_BASE_URL = 'http://trust-uat.paytm.in'
PAYTM_WALLET_NAME = ""

#Android
LOCALYTICS_ANDROID_API_KEY = "7538defbb583b2640de0dc2-af993e68-23ed-11e6-44b0-00adad38bc8d"
LOCALYTICS_ANDROID_APP_SECRET = "6bf73d0bd5b9d46e5dc606d-af9941b0-23ed-11e6-44b0-00adad38bc8d"
LOCALYTICS_ANDROID_APP_ID = "cb7d78068b3a8eef7776e44-a2880d00-78af-11e6-d3c4-001660e79be1"

#iphone
LOCALYTICS_IPHONE_API_KEY = ""
LOCALYTICS_IPHONE_APP_SECRET = ""
LOCALYTICS_IPHONE_APP_ID = "bacbac8c26ba7299bc691b2-9c04113c-920f-11e6-fd8f-00ae30fe7875"

SEND_STATUS_CHANGE_TO_LOCALYTICS = False
