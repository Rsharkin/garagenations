from core.models.common import CreatedAtAbstractBase
from core.models.booking import Booking
from core.models.master import Notifications
from core.constants import ACTION_DICT
from django.db import models
from django.conf import settings


class Messages(CreatedAtAbstractBase):
    """
        Tables for sent notification like sms/Email/push
    """
    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        ordering = ['-id']

    MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER = 1
    MESSAGE_DIRECTION_BUMPER_TO_DEALER = 2
    MESSAGE_DIRECTION_CUSTOMER_TO_DEALER = 3
    MESSAGE_DIRECTION_DEALER_TO_CUSTOMER = 4
    MESSAGE_DIRECTION_BUMPER_TO_OPS = 5

    MESSAGE_DIRECTION_TYPE = (
        (MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER, 'BumperToCustomer'),
        (MESSAGE_DIRECTION_BUMPER_TO_DEALER, 'BumperToDealer'),
        (MESSAGE_DIRECTION_CUSTOMER_TO_DEALER, 'CustomerToDealer'),
        (MESSAGE_DIRECTION_DEALER_TO_CUSTOMER, 'DealerToCustomer'),
        (MESSAGE_DIRECTION_BUMPER_TO_OPS, 'BumperToOps'),
        )

    MESSAGE_SEND_LEVEL_ALL = 1
    MESSAGE_SEND_LEVEL_SPECIFIC = 2
    MESSAGE_SEND_LEVELS = (
        (MESSAGE_SEND_LEVEL_ALL, 'All'),
        (MESSAGE_SEND_LEVEL_SPECIFIC, 'Specific'),
    )

    MESSAGE_TYPE_SMS = 1
    MESSAGE_TYPE_PUSH = 2
    MESSAGE_TYPE_EMAIL = 3

    MESSAGE_TYPES = (
        (MESSAGE_TYPE_SMS, 'SMS'),
        (MESSAGE_TYPE_EMAIL, 'EMAIL'),
        (MESSAGE_TYPE_PUSH, 'PUSH'),
    )

    LABEL_STATUS = 1
    LABEL_FEEDBACK = 2
    LABEL_UPDATE = 3
    LABEL_OFFER = 4
    LABEL_REFERRAL = 5
    LABEL_RATE_US = 6
    LABEL_FILL_PROFILE = 7
    LABEL_FILL_CAR_INFO = 8
    LABEL_EOD = 9
    LABEL_REQUEST_LOCATION = 10
    LABEL_CANCEL_RETARGET = 11
    LABEL_ADDED_TO_CART_RETARGET = 12

    LABEL_TYPES = (
        (LABEL_STATUS, 'Status'),
        (LABEL_FEEDBACK, 'Feedback'),
        (LABEL_UPDATE, 'Update'),
        (LABEL_OFFER, 'Offer'),
        (LABEL_REFERRAL, 'Referral'),
        (LABEL_RATE_US, 'RateUs'),
        (LABEL_FILL_PROFILE, 'FillProfile'),
        (LABEL_FILL_CAR_INFO, 'FillCarInfo'),
        (LABEL_EOD, 'EOD'),
        (LABEL_REQUEST_LOCATION, 'Req. Loc.'),
        (LABEL_CANCEL_RETARGET, 'CancelRetarget'),
        (LABEL_ADDED_TO_CART_RETARGET, 'AddToCartRetarget'),
    )

    message_type = models.SmallIntegerField(choices=MESSAGE_TYPES, null=False, help_text="Type of message.")
    subject = models.CharField(max_length=256, null=True)
    message = models.TextField(null=True, blank=True, help_text="This will be empty for email where content of email "
                                                                "is not stored.")
    message_send_level = models.SmallIntegerField(null=False, choices=MESSAGE_SEND_LEVELS,
                                                  default=MESSAGE_SEND_LEVEL_ALL)
    direction = models.SmallIntegerField(null=False,choices=MESSAGE_DIRECTION_TYPE)
    viewed_by = models.IntegerField(default=0, help_text="Will be updated once user views the message."
                                                         "(For push notifications only)")
    booking = models.ForeignKey(Booking, null=True, blank=True, related_name='message_booking')
    action = models.SmallIntegerField(choices= tuple((item, item) for item in list(ACTION_DICT.keys())), null=True, blank=True)
    notification = models.ForeignKey(Notifications, null=True, blank=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='message_sent_by', null=True, blank=True,
                                help_text="This is reference to user how has triggered the notification or sent the "
                                          "notification.")
    label = models.PositiveSmallIntegerField(choices=LABEL_TYPES, null=True,
                                             help_text='This is to identify which screen will open in UI')


class MessageUser(CreatedAtAbstractBase):
    """
        Mapping of message to individual users.
    """
    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        ordering = ['-id']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='message_user', null=True, blank=True,
                             help_text="Will be empty when sending mail/sms directly to email or sms like for OPS mails")
    message = models.ForeignKey(Messages, null=False, related_name='user_message')
    sent_to = models.CharField(max_length=1024, null=True, help_text="Phone number for SMS, email address for email. "
                                                                    "Null in case of push notifications")
    gateway_api_response = models.CharField(max_length=64, null=True)
    delivery_report = models.CharField(max_length=64, null=True, blank=True)
    delivered_dt = models.DateTimeField(null=True, help_text='Timestamp of delivery or receipt of delivery.')
    retry_count = models.IntegerField(default=0, null=True, help_text="Number of tries to send in case of failure.")
    viewed_dt = models.DateTimeField(null=True, help_text='This is when mobile user reads the msg.')
