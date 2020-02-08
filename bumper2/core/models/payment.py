from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.constants import SMS_TEMPLATES, SMS_TEMPLATE_PAYMENT_SUCCESS_OPS
from core.models.common import CreatedAtAbstractBase
from core.models.booking import Booking, BookingInvoice, BookingProformaInvoice
import logging
logger = logging.getLogger(__name__)

class Payment(CreatedAtAbstractBase):
    """
        Model to hold Payment Transactions.
    """
    PAYMENT_MODE_CASH = 1
    PAYMENT_MODE_ONLINE = 2
    PAYMENT_MODE_EMAIL_LINK = 3
    PAYMENT_MODE_SMS_LINK = 4
    PAYMENT_MODE_CHEQUE = 5
    PAYMENT_MODE_POS = 6
    PAYMENT_MODE_BANK_TRANSFER = 7

    PAYMENT_MODES = (
        (PAYMENT_MODE_CASH, 'Cash'),
        (PAYMENT_MODE_ONLINE, 'Online'),
        (PAYMENT_MODE_EMAIL_LINK, 'Email Invoice'),
        (PAYMENT_MODE_SMS_LINK, 'SMS Link'),
        (PAYMENT_MODE_CHEQUE, 'Cheque'),
        (PAYMENT_MODE_POS, 'POS'),
        (PAYMENT_MODE_BANK_TRANSFER, 'Bank Transfer'),
    )

    VENDOR_PAYU_MONEY = 'PayUMoney'
    VENDOR_BUMPER = 'bumper'  # payment was collected by bumper executive
    VENDOR_USER_TO_DEALER = 'UserToDealer'  # payment was collected by bumper executive
    VENDOR_BUMPER_CITIBANK = 'BumperCitibank'  # This is for payment to dealer and should be shown
    VENDOR_MSWIPE = 'MSwipe'
    VENDOR_CITRUS_PAY = 'Citrus'
    VENDOR_RAZOR_PAY = 'RazorPay'
    # only in dealer payment.

    VENDOR_LIST = (
        (VENDOR_CITRUS_PAY, 'By Citrus Pay'),
        (VENDOR_PAYU_MONEY, 'By PayU Money'),
        (VENDOR_BUMPER, 'Bumper Executive'),
        (VENDOR_USER_TO_DEALER, 'User to Dealer Directly'),
        (VENDOR_BUMPER_CITIBANK, 'By Bumper Citibank'),
        (VENDOR_MSWIPE, 'MSwipe POS'),
        (VENDOR_RAZOR_PAY, 'RazorPay'),
    )

    TX_STATUS_SUCCESS = 1
    TX_STATUS_FAILED = 2
    TX_STATUS_PENDING = 3   # this state is used for dealer payment when ops has entered the payment
                                    # but it is not paid by Akhil to dealer.

    TX_STATUSES = (
        (TX_STATUS_SUCCESS, 'Success'),
        (TX_STATUS_FAILED, 'Failed'),
        (TX_STATUS_PENDING, 'Pending'),
    )

    TX_TYPE_PAYMENT = 1
    TX_TYPE_REFUND = 2
    TX_TYPE_VOID = 3
    TX_TYPES = (
        (TX_TYPE_PAYMENT, 'Payment'),
        (TX_TYPE_REFUND, 'Refund'),
        (TX_TYPE_VOID, 'Void')
    )
    PAYMENT_FOR_USER = 'user'
    PAYMENT_FOR_DEALER = 'dealer'

    PAYMENT_FOR_TYPES = (
        (PAYMENT_FOR_USER, 'User'),
        (PAYMENT_FOR_DEALER, 'Dealer'),
    )

    PAYMENT_TYPE_NOW = 1
    PAYMENT_TYPE_COD = 2

    PAYMENT_TYPES = (
        (PAYMENT_TYPE_NOW,"Pay Now"),
        (PAYMENT_TYPE_COD,"Cash on Delivery"),
    )

    payment_for = models.CharField(max_length=6, null=False, blank=False, default=PAYMENT_FOR_USER, db_index=True)
    payment_type = models.PositiveSmallIntegerField(null=False, blank=False,default=PAYMENT_TYPE_COD, choices=PAYMENT_TYPES)
    tx_status = models.IntegerField(null=False, blank=False, choices=TX_STATUSES,default=TX_STATUS_PENDING)
    tx_type = models.SmallIntegerField(default=TX_TYPE_PAYMENT, null=False, blank=False, choices=TX_TYPES)
    #booking = models.ForeignKey(Booking, null=True, blank=True,related_name='booking_payment')
    invoice = models.ForeignKey(BookingInvoice, null=True, blank=True,related_name='invoice_payment')
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.00, null=True, blank=True)
    mode = models.SmallIntegerField(null=False, blank=False, choices=PAYMENT_MODES, default=PAYMENT_MODE_ONLINE)
    vendor = models.CharField(max_length=16, null=True, blank=True, choices=VENDOR_LIST)
    payment_vendor_id = models.CharField(max_length=128, null=True, blank=True,
                                         help_text="This is payuMoneyId in case of PayU. This will be null in case "
                                                   "of cash payments")
    refund_vendor_id = models.CharField(max_length=128, null=True, blank=True,
                                         help_text="Refund for payment, Vendor ID")
    vendor_status = models.CharField(max_length=64, null=True, blank=True)
    error_message = models.CharField(max_length=256, null=True, blank=True,
                                     help_text="This will reflect error msg from payment gateway if any.")
    cheque_num = models.CharField(max_length=20, null=True, blank=True)
    cheque_bank = models.CharField(max_length=32, null=True, blank=True)
    tx_data = models.TextField(null=True, blank=True)
    merchant_trx_id = models.CharField(max_length=32, null=True, blank=True)
    device_type = models.CharField(max_length=12, null=True, blank=True)
    proforma_invoice = models.ForeignKey(BookingProformaInvoice, null=True, blank=True,related_name='proforma_invoice_payment')

    history = HistoricalRecords()

    def __str__(self):
        return "%s" % self.id

    def __unicode__(self):
        return "%s" % self.id


class CreditMemo(CreatedAtAbstractBase):
    """
        Model to store credit memo against refunds
    """
    #booking = models.ForeignKey(Booking, null=True, blank=True,related_name='booking_credit_memo')
    invoice = models.ForeignKey(BookingInvoice, null=True, blank=True,related_name='invoice_credit_memo')
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.00, null=True, blank=True)

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    try:
        if instance.payment_for == Payment.PAYMENT_FOR_USER \
                and instance.tx_status == Payment.TX_STATUS_SUCCESS:
            if instance.tx_type == Payment.TX_TYPE_PAYMENT:
                from core.tasks import process_hooks
                from core.constants import ACTION_PAYMENT_RECEIVED
                from core.tasks import send_async_sms
                from core.managers.bookingManager import get_bill_details_new
                invoice = instance.invoice
                if not invoice:
                    invoice = instance.proforma_invoice
                bill_details = get_bill_details_new(invoice.booking)

                process_hooks.delay(invoice.booking.id, ACTION_PAYMENT_RECEIVED,
                                    {'amt_paid': str(bill_details.get('payable_amt'))})

                number_to_send_to = settings.ALERT_SMS_PAYMENT_SUCCESSFUL
                driver = invoice.booking.drop_driver
                if driver and driver.ops_phone:
                    number_to_send_to.append(driver.ops_phone)

                sms_text = SMS_TEMPLATES[SMS_TEMPLATE_PAYMENT_SUCCESS_OPS] % ({
                    'amt_paid': instance.amount,
                    'booking_id': invoice.booking_id,
                    'payable': bill_details.get('payable_amt'),
                    'payment_mode': dict(Payment.PAYMENT_MODES)[instance.mode] if instance.mode else '',
                    'payment_status': dict(Payment.TX_STATUSES)[instance.tx_status] if instance.tx_status else '',
                    'payment_type': "%s-%s" % (instance.vendor, instance.vendor_status) if instance.vendor else '',
                })
                send_async_sms.delay(invoice.booking.user_id, number_to_send_to, sms_text)
            elif instance.tx_type == Payment.TX_TYPE_REFUND and created:
                CreditMemo.objects.create(amount=instance.amount, invoice=instance.invoice)
    except:
        logger.exception('Failed to send alert for payment success.')
