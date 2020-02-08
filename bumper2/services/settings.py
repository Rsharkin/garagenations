# -*- coding: utf-8 -*-

from django.conf import settings

# Trello settings
TRELLO_API_KEY = '42d241b099c8cc627e784b68215e25e1'
TRELLO_API_SECRET = '473efb163adb267dcbfbfd22a3a67d36f7111a72b0b87cbab5eaaa2bc9b28402'
TRELLO_OAUTH_TOKEN = '0a5d91e62af5980cc731399095eab502e494c69acf82953505a162d5ffb26323'
TRELLO_OAUTH_TOKEN_SECRET = ''


#### Setting to boto s3
AWS_ACCESS_KEY_ID = 'AKIAJBCFWACGIRZ3IA5A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_ACL_POLICY = 'public-read'
BOTO_S3_BUCKET = 'unbox-bumper'
BOTO_S3_BUCKET_STATIC = 'unbox-bumper-static'
BOTO_S3_HOST = 's3.amazonaws.com'
BOTO_BUCKET_LOCATION = 'DEFAULT'
AWS_S3_FORCE_HTTP_URL = False
####

### settings for cognito based login in aws.

COGNITO_AWS_REGION = 'eu-west-1'
COGNITO_ACCESS_KEY_ID = 'AKIAJ322T2UW7IMAEXOA'
COGNITO_SECRET_ACCESS_KEY = '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'

if settings.BUMPER_ENV == 'PROD':
    IDENTITY_POOL_ID = 'eu-west-1:a5d2baa5-6acc-4bd1-bcda-4a1080824a83'
    DEVELOPER_PROVIDED_NAME = 'auth.bumper.com'
else:
    IDENTITY_POOL_ID = 'eu-west-1:d3582f70-7089-4742-b84f-3cf5339643cc'
    DEVELOPER_PROVIDED_NAME = 'auth.staging.bumper.com'

# TOKEN_DURATION = 3400 # can be set keeping it default to 15 mins for now.
###

FCM_DJANGO_SETTINGS = getattr(settings, "FCM_DJANGO_SETTINGS", {})

# FCM
FCM_DJANGO_SETTINGS.setdefault("FCM_SERVER", "https://fcm.googleapis.com/fcm/send")
FCM_DJANGO_SETTINGS.setdefault("FCM_SERVER_KEY", "AAAAzPBZSOg:APA91bGGGNif42bt46FSK0J_E6N22KkpN6-qgZdXamVFL2Bntid8gOow1L5XP6iVPHNb_hZMyayVxJgj2JGoMx4ROWX1-r7o8Vt7YMKJiZevcVnjqbgbz5L2esPaL0puizjwSx101iMe")

FCM_DJANGO_SETTINGS.setdefault("ERRORS", {
    'invalid_registration': 'InvalidRegistration',
    'missing_registration': 'MissingRegistration',
    'not_registered': 'NotRegistered',
    'invalid_package_name': 'InvalidPackageName'
})

### Setting for SES email service
SES_REGION_NAME = "eu-west-1"
SES_REGION_ENDPOINT = "email.eu-west-1.amazonaws.com"
SES_ACCESS_KEY_ID = 'AKIAIT23B5QMUZZMX7GA'
SES_SECRET_ACCESS_KEY = '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'

#DEFAULT_FROM_EMAIL = 'noreply@bumper.com'
DEFAULT_FROM_EMAIL = 'bumpercare@bumper.com'
## SES/Mail settings:
"""
SMTP Username:
AKIAISG6R3E7NQQYXWQQ
SMTP Password:
AtMAPMMcc8S9AO1FsFB3qE39Q/bgCAxihS9TzV3T2ZQV

Server Name:
email-smtp.eu-west-1.amazonaws.com
Port:    25, 465 or 587
Use Transport Layer Security (TLS):    Yes

"""

# Setting choose email provider.
SMS_PROVIDER = "MANDRILL"  # options are ['MANDRILL', 'SES']
