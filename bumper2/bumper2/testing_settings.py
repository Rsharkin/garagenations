# -*- coding: utf-8 -*-

from bumper2.settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testing_bumper2',
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
    "APNS_CERTIFICATE": "deployment/bumperDev.pem",
}

ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST = ['praveena@bumper.com', 'pravin.raj@bumper.com', 'deepakraj@bumper.com',
                                       'veeresh@bumper.com', 'rishi.sharma@bumper.com', 'anuj@bumper.com']


ALERT_SMS_PAYMENT_SUCCESSFUL = [
    '8800165656',  # Inderjeet
]

SMS_FAILURE_ALERT_LIST = ['inderjeet@autoninja.in', 'anuj@autoninja.in']

CITRUS_MERCHANT_ACCESS_KEY = 'ATJP15ZY1GDG0VAAHQXX'
CITRUS_MERCHANT_SECRET_KEY = 'e048d67c7541fd422cec0395e50169d1ed422e0f'
CITRUS_RETURN_URL = 'http://testing.bumper.com/payment/citrus-pay/'
CITRUS_WEBSITE_RETURN_URL = 'http://testing.bumper.com/payment/citrus-pay-web/'
CITRUS_VANITY_URL = 'mvw7nadn8e'
CITRUS_FORM_POST_URL = "https://www.sandbox.citruspay.com/%s" % CITRUS_VANITY_URL

BASE_URL = 'http://testing.bumper.com/'

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/2'

OPBEAT = {
    'debug': True,
    'ORGANIZATION_ID': '8e41e3be8eea4489b118bd9dff00188c',
    'APP_ID': '2679047dae',
    'SECRET_TOKEN': 'd4a2f6ce3eaed82aadc646c3d374c0f09286291d',
}
OPBEAT_WEBSITE = {
    'debug': True,
    'ORGANIZATION_ID': '8e41e3be8eea4489b118bd9dff00188c',
    'APP_ID': 'b199cf0a1b',
    'SECRET_TOKEN': 'd4a2f6ce3eaed82aadc646c3d374c0f09286291d',
}

LOCALYTICS_KEY = ""
GOOGLE_ANALYTICS_UNIVERSAL_KEY = ""

LOGGING_FOLDER = '/var/log/bumper2/testing/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_FOLDER + 'bump.log',
            'maxBytes': 1024*1024*100, # 100 MB
            'backupCount': 15,
            'formatter':'standard',
        },
        'script': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_FOLDER + 'scripts_bump.log',
            'maxBytes': 1024*1024*100, # 100 MB
            'backupCount': 15,
            'formatter': 'standard',
        },
        'request_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': LOGGING_FOLDER + 'django_request.log',
                'maxBytes': 1024*1024*100, # 100 MB
                'backupCount': 15,
                'formatter':'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'bumper.scripts': {
            'handlers': ['script'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django': {
            'handlers': ['mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}