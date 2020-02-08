from django.conf import settings
from django.db import transaction
from core.models.payment import Payment
from core.models.booking import Booking, BookingInvoice, BookingProformaInvoice
from core.models.users import CreditTransaction, UserCredit

import decimal
import logging
logger = logging.getLogger(__name__)


def deduct_user_credits(user, credit, entity, entity_id, reason):
    with transaction.atomic():
        CreditTransaction.objects.create(user=user, amount=credit,
                                         trans_type=CreditTransaction.TRANSACTION_TYPE_DEBIT,
                                         entity=entity,
                                         entity_id=entity_id, reason=reason)
        uc, created = UserCredit.objects.get_or_create(user=user, defaults={"credit": 0})
        uc.credit -= credit
        uc.save()
        logger.info(
            "Credits Deducted - entity-{}, entity_id-{}, User-{}, Reason-{}".format(
                entity,
                entity_id,
                user.id,
                reason))


def process_payment_response(payment_dict, vendor_tx_data):
    from core.tasks import send_async_new_email_service
    from core.models import Messages

    booking_id = ''
    try:
        vendor_id = payment_dict.get('vendor_id')
        booking_id = payment_dict.get('booking_id')
        payment_id = payment_dict.get('payment_id')
        net_amount_debit = payment_dict.get('net_amount_debit')
        invoice_id = payment_dict.get('invoice_id')
        proforma_invoice_id = payment_dict.get('proforma_invoice_id')
        status = payment_dict.get('status')
        vendor_status = payment_dict.get('vendor_status', status)
        error_message = payment_dict.get('error_message', None)
        vendor = payment_dict.get('vendor')
        mode = payment_dict.get('mode')
        device_type = payment_dict.get('device_type')
        tx_type = payment_dict.get('tx_type', Payment.TX_TYPE_PAYMENT)
        cheque_num = payment_dict.get('cheque_num')
        cheque_bank = payment_dict.get('cheque_bank')
        used_credits = payment_dict.get('used_credits', '0.00')

        missing_critical_data = False
        if not vendor_id:
            missing_critical_data = True
            logger.error('Payment does not have Vendor Id.')
            send_async_new_email_service.delay(
                to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
                cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
                subject='Bumper: Payment Gateway Issue.[BookingID:%s]' % booking_id,
                body='Payment Data does not have Vendor Id.<br><br>Data Returned=%s' % str(vendor_tx_data),
                email_format='html',
                message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                analytic_info={
                    'booking_id': booking_id
                }
            )

        if not booking_id:
            missing_critical_data = True
            logger.error('Payment does not have booking ID.')
            if vendor_id:
                send_async_new_email_service.delay(
                    to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
                    cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
                    subject='Bumper: Payment Gateway Issue.[BookingID:%s]' % booking_id,
                    body='Payment Data does not have Booking Id.<br><br>Data Returned=%s'% str(vendor_tx_data),
                    email_format='html',
                    message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS
                )

        # if not payment_id:
        #     missing_critical_data = True
        #     logger.error('Payment does not have payment ID.')
        #     if vendor_id:
        #         send_async_new_email_service.delay(
        #             to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
        #             cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
        #             subject='Bumper: Payment Gateway Issue.[BookingID:%s]' % booking_id,
        #             body='Payment Data does not have Payment Id.<br><br>Data Returned=%s'% str(vendor_tx_data),
        #             email_format='html',
        #             message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
        #             analytic_info={
        #                 'booking_id': booking_id
        #             }
        #         )

        if not missing_critical_data:
            status_to_save = Payment.TX_STATUS_SUCCESS
            if status != "success":
                logger.error('Payment Failed/Cancelled on Payment Gateway')
                send_async_new_email_service.delay(
                    to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
                    cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
                    subject='Bumper: Payment Failed/Cancelled on Payment Gateway.[BookingID:%s]' % booking_id,
                    body='Payment Failed/Cancelled on Payment Gateway.<br><br>Error Message=%s<br><br>Data Returned=%s'
                         % (error_message, str(vendor_tx_data)),
                    email_format='html',
                    message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                    analytic_info={
                        'booking_id': booking_id
                    })
                status_to_save = Payment.TX_STATUS_FAILED

            invoice = None
            proforma_invoice = None
            payment_filter_dict = {
                'tx_status': Payment.TX_STATUS_PENDING
            }
            if invoice_id:
                invoice = BookingInvoice.objects.filter(id=invoice_id,
                                                        status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                    BookingInvoice.INVOICE_STATUS_PAID]
                                                        ).first()
            if proforma_invoice_id:
                proforma_invoice = BookingProformaInvoice.objects.filter(id=proforma_invoice_id,
                                                      status = BookingProformaInvoice.INVOICE_STATUS_PENDING
                                                      ).first()

            if not proforma_invoice and not invoice:
                invoice = BookingInvoice.objects.filter(booking_id=booking_id,
                                                        status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                    BookingInvoice.INVOICE_STATUS_PAID]).first()
                if not invoice:
                    proforma_invoice = BookingProformaInvoice.objects.filter(
                                        booking_id=booking_id,
                                        status=BookingProformaInvoice.INVOICE_STATUS_PENDING).first()

            if proforma_invoice:
                payment_filter_dict['proforma_invoice'] = proforma_invoice
            else:
                payment_filter_dict['invoice'] = invoice

            old_payment = Payment.objects.filter(**payment_filter_dict).order_by('-created_at').first()

            try:
                import ujson
                data_json = ujson.dumps(vendor_tx_data)
            except:
                data_json = {"Error":"Error in processing payment response."}
                logger.exception('Failed to dump data')
                send_async_new_email_service.delay(
                    to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
                    cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
                    subject='Bumper: Payment Gateway Issue. Unable to Dump data [BookingID:%s]' % booking_id,
                    body='Unable to dump data',
                    email_format='html',
                    message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                    analytic_info={
                        'booking_id': booking_id
                    })
            if not mode:
                mode = Payment.PAYMENT_MODE_ONLINE
            if old_payment:
                if old_payment.tx_status != Payment.TX_STATUS_PENDING:
                    logger.info('Payment already proccessed once Tx Id: %s Old status=%s' % (str(vendor_id),
                                                                                            old_payment.tx_status))
                else:
                    logger.info('Payment Tx Id: %s Old status=%s' % (str(vendor_id), old_payment.tx_status))
                old_payment.tx_status = status_to_save
                old_payment.vendor_status = vendor_status
                old_payment.amount = net_amount_debit
                old_payment.error_message = error_message
                old_payment.tx_data = data_json
                old_payment.mode = mode
                old_payment.vendor = vendor
                old_payment.device_type = device_type
                old_payment.invoice = invoice
                old_payment.proforma_invoce = proforma_invoice
                old_payment.tx_type = tx_type
                old_payment.cheque_num = cheque_num
                old_payment.cheque_bank = cheque_bank
                old_payment.save()
            else:
                # create invoice if does not exist - Let's see if there is such case or not.
                old_payment = Payment.objects.create(
                    invoice=invoice,
                    proforma_invoice=proforma_invoice,
                    tx_status=status_to_save,
                    vendor_status=vendor_status,
                    mode=mode,
                    vendor=vendor,
                    amount=net_amount_debit,
                    payment_vendor_id=vendor_id,
                    error_message=error_message,
                    tx_data=data_json,
                    device_type=device_type,
                    tx_type=tx_type
                )
            if status == "success":
                b = Booking.objects.get(id=booking_id)
                if used_credits:
                    used_credits = decimal.Decimal(used_credits)
                    if used_credits > 0:
                        debit_reason = "Credits debited along with payment id: {}".format(old_payment.id)
                        deduct_user_credits(b.user, used_credits, CreditTransaction.ENTITY_BOOKING,
                                            b.id, debit_reason)

                if invoice:
                    all_payments = Payment.objects.filter(invoice=invoice, tx_status=Payment.TX_STATUS_SUCCESS)
                    total_amount_received = decimal.Decimal('0.00')
                    if used_credits:
                        total_amount_received += decimal.Decimal(used_credits)
                    for p in all_payments:
                        total_amount_received += p.amount
                    if total_amount_received >= invoice.payable_amt:
                        invoice.status = BookingInvoice.INVOICE_STATUS_PAID
                        invoice.save()
                if proforma_invoice:
                    proforma_invoice.status = BookingProformaInvoice.INVOICE_STATUS_PAID
                    proforma_invoice.save()

                #b.status_id = 17
                #b.save()
                if old_payment.payment_type != Payment.PAYMENT_TYPE_COD:
                    if b.is_doorstep:
                        b.status_id = 21
                    else:
                        b.status_id = 18
                    b.save()

                booking_coupons = b.booking_coupon.all()
                for bc in booking_coupons:
                    bc.is_paid = True
                    bc.save()
                from core.tasks import process_hooks
                #from core.managers.generalManager import process_hooks

                # proper notification for proforma invoice
                process_hooks.delay(b.id, 17)
                process_hooks.delay(b.id, 52, {'amt_paid': old_payment.amount})
            if old_payment:
                return old_payment.id
            return True
    except Exception as e:
        logger.exception('Failed to save payment details.')
        send_async_new_email_service.delay(
            to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
            cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
            subject='Bumper: Payment Gateway Issue.[BookingID:%s]' % booking_id,
            body='Processing of payment failed.<br><br>Exception=%s<br><br>Data Returned=%s' % (str(e),str(vendor_tx_data)),
            email_format='html',
            message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
            analytic_info={
                'booking_id': booking_id
            })
    return False


def get_payment_details(booking_obj):
    payment_details = {}
    payment_details['pending_payment_id'] = None

    payments = []
    pending_invoice_payments = []
    booking_invoices = booking_obj.booking_invoice.all()
    for booking_invoice in booking_invoices:
        if hasattr(booking_invoice,'payments'):
            payments = payments + booking_invoice.payments
            if booking_invoice.status == BookingInvoice.INVOICE_STATUS_PENDING:
                pending_invoice_payments += booking_invoice.payments

    booking_proforma_invoices = booking_obj.booking_proforma_invoice.all()
    for booking_proforma_invoice in booking_proforma_invoices:
        if hasattr(booking_proforma_invoice,'proforma_payments'):
            payments = payments + booking_proforma_invoice.proforma_payments
            if booking_proforma_invoice.status == BookingProformaInvoice.INVOICE_STATUS_PENDING:
                pending_invoice_payments += booking_proforma_invoice.proforma_payments

    #if hasattr(booking_obj, 'payments'):
    #    payments = booking_obj.payments

    pending_payment = (pending_invoice_payments or [None])[0]
    if pending_payment and pending_payment.payment_type == Payment.PAYMENT_TYPE_COD \
            and pending_payment.tx_status==Payment.TX_STATUS_PENDING \
            and pending_payment.tx_type == Payment.TX_TYPE_PAYMENT:
        payment_details['pending_payment_id'] = pending_payment.id

    #payment_status = Payment.TX_STATUS_PENDING

    latest_payment = None
    for payment in payments:
        if payment.tx_status == Payment.TX_STATUS_SUCCESS:
            latest_payment = payment
            break
        elif payment.tx_status == Payment.TX_STATUS_FAILED:
            latest_payment = payment

    from api.serializers.bookingSerializers import PaymentSerializer

    payment_details['payment'] = {}
    if not latest_payment:
        latest_payment = pending_payment
    if latest_payment:
        payment_details['payment'] = PaymentSerializer(latest_payment,remove_fields=[
                                                       'tx_data',
                                                       'tx_type',
                                                       'payment_for',
                                                       'vendor',
                                                       'payment_vendor_id',
                                                       'refund_vendor_id',
                                                       'vendor_status',
                                                       'cheque_num',
                                                       'cheque_bank']).data

    return payment_details


def get_payments(booking_obj):
    from api.serializers.bookingSerializers import PaymentSerializer
    payments = []
    booking_invoices = booking_obj.booking_invoice.all()
    booking_proforma_invoices = booking_obj.booking_proforma_invoice.all()
    for booking_invoice in booking_invoices:
        if hasattr(booking_invoice,'payments'):
            payments = payments + booking_invoice.payments

    for booking_proforma_invoice in booking_proforma_invoices:
        if hasattr(booking_proforma_invoice,'proforma_payments'):
            updated_payments = []
            for payment in booking_proforma_invoice.proforma_payments:
                if not payment.invoice_id:
                    updated_payments.append(payment)
            payments = payments + updated_payments

    payment_serializer = PaymentSerializer(payments, many=True)
    return payment_serializer.data
