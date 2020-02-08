
import boto.ses
from . import settings
import mandrill
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


class EmailService(object):
    """
        Class to hold the business logic for sending email,
         currently putting in SES sending mail for quick execution.
         TODO:
            1) Add maindrill and mailchimp support
    """
    def __init__(self, notice_type=None):
        self.status = True
        self.notice_type = notice_type

    @staticmethod
    def _make_connection():
        # region = RegionInfo(None, settings.SES_REGION_NAME, settings.SES_REGION_ENDPOINT)
        conn = boto.ses.connect_to_region(settings.SES_REGION_NAME, aws_access_key_id=settings.SES_ACCESS_KEY_ID,
                                           aws_secret_access_key=settings.SES_SECRET_ACCESS_KEY)
        log.info('connection: %s' % conn.list_verified_email_addresses())
        return conn

    @staticmethod
    def send_email(email_subject, email_body, to_address_list, cc_address_list=None, bcc_address_list=None,
                   email_format='text', sender='Bumper.com <%s>' % settings.DEFAULT_FROM_EMAIL, *args, **kwargs):
        """
            this will be used to send email through AWS.
        :param email_subject:
        :param email_body:
        :param to_address_list:
        :param cc_address_list:
        :param bcc_address_list:
        :param email_format:
        :param sender:
        :param args:
        :param kwargs:
        :return:
        """
        if not sender:
            sender = 'Bumper.com <%s>' % settings.DEFAULT_FROM_EMAIL
        if not email_format:
            email_format = 'text'
        if not cc_address_list:
            cc_address_list = []

        conn = EmailService._make_connection()
        status = conn.send_email(sender,
                        email_subject,
                        email_body,
                        to_address_list,
                        cc_addresses=cc_address_list,
                        bcc_addresses=bcc_address_list,
                        format=email_format,
                        return_path=sender,
                        reply_addresses=[settings.DEFAULT_FROM_EMAIL])
        log.info('status of email: %s' % status)
        conn.close()
        return status

    # TODO put mandril in place .. Do not delete this code.
    # @staticmethod
    # def send_mail_using_mandrill(to_email, template_name, var_list=[], template_content=[], bcc_list=None, subject=None):
    #     """
    #         var_list = [{'name':'NAME','content': 'merge2'}]
    #     :param to_email:
    #     :param template_name:
    #     :param var_list:
    #     :param template_content:
    #     :return:
    #     """
    #     if bcc_list is None:
    #         bcc_list = []
    #     to_list = [{'email': to_email, 'type': 'to','name': ''}]
    #     merge_vars_list = [{'rcpt': to_email,'vars': var_list}]
    #     for email in bcc_list:
    #         to_list.append({'email': email, 'type': 'bcc','name': ''})
    #         merge_vars_list.append({'rcpt': email,'vars': var_list})
    #     #mandrill_client = mandrill.Mandrill('tAVZ-68DZLIL4usdU4jQag')
    #     mandrill_client = mandrill.Mandrill('jkr7q7m8hKvLfbtrvcXXSA')
    #     message = {'to': to_list,
    #                'merge_vars':merge_vars_list,
    #                }
    #     if subject:
    #         message['subject'] = subject
    #
    #     response = mandrill_client.messages.send_template(template_name=template_name, template_content=template_content,
    #                                            message=message, async=False)
    #
    #     log.debug('Mandrill response: %s' % str(response))
    #     return response


    @staticmethod
    def send_mail_using_mandrill_without_template(subject, to_email_list, body, cc_email_list=[], attachments=[],
                                                  from_email = settings.DEFAULT_FROM_EMAIL, from_name="Bumper.com"):
        """
            var_list = [{'name':'NAME','content': 'merge2'}]
        :param to_email:
        :param template_name:
        :param var_list:
        :param template_content:
        :return:

        message = {'attachments': [{'content': 'ZXhhbXBsZSBmaWxl', 'name': 'myfile.txt', 'type': 'text/plain'}],}
        attachments: [{'content': 'ZXhhbXBsZSBmaWxl', 'name': 'myfile.txt', 'type': 'text/plain'}],
        to: [{'email': to_email, 'type': 'to', 'name': ''}],
        """
        #mandrill_client = mandrill.Mandrill('tAVZ-68DZLIL4usdU4jQag')
        to_list = []
        for item in to_email_list:
            to_list.append({
                'email': item,
                'name': str(item).split('@')[0],
                'type': 'to',
            })

        for item in cc_email_list:
            to_list.append({
                'email': item,
                'name': str(item).split('@')[0],
                'type': 'cc',
            })

        mandrill_client = mandrill.Mandrill('jkr7q7m8hKvLfbtrvcXXSA')
        message = {
            'to': to_list,
            'bcc_address': settings.DEFAULT_FROM_EMAIL,
            'from_email': from_email,
            'from_name': from_name,
            'preserve_recipients': True,
            'headers': {'Reply-To': settings.DEFAULT_FROM_EMAIL},
            'html': body,
            'subject': subject,
            'attachments': attachments,
        }

        log.debug('Mandrill request Obj: %s' % str(message))
        response = mandrill_client.messages.send(message=message, async=False)
        log.debug('Mandrill response: %s' % str(response))
        return response


class NewEmailService(object):
    """
        Class to use new django ses to send out mails to customers.
        base_template_folder = 'mailers-template'
        for each mailer there should be folder in mailers-template with three templates
        1. mail-html
        2. subject-text
        3. mail-text

    """
    def __init__(self, to_list, cc_list=[], bcc_list=[], context={}, sender=settings.DEFAULT_FROM_EMAIL,
                 email_format='text', analytic_info={}, message_direction=1, from_name="Bumper.com"):
        """
            TODO: Fix Bumper.com <%s> sender
        :param to_list:
        :param cc_list:
        :param bcc_list:
        :param context:
        :param sender:
        :param email_format:
        :param analytic_info:
        :param message_direction:
        """
        self.base_template_name = 'mailers-template'
        self.to = [to_list] if isinstance(to_list, basestring) else to_list
        self.reply_to = sender
        self.from_email = sender
        self.from_name = from_name
        self.cc_list = [cc_list] if isinstance(cc_list, basestring) else cc_list
        self.bcc_list = [bcc_list] if isinstance(bcc_list, basestring) else bcc_list
        self.context = context
        self.email_format = email_format
        self.analytic_info = analytic_info
        self.direction = message_direction
        self._html = None
        self._text = None
        self._subject = None

    def _build_template_path(self, template_folder_name):
        html_template = '%s/%s/body.html' % (self.base_template_name, template_folder_name)
        subject_text = '%s/%s/subject.txt' % (self.base_template_name, template_folder_name)
        text_template = '%s/%s/text.txt' % (self.base_template_name, template_folder_name)
        return html_template, subject_text, text_template

    def _render(self, template, context):
        return render_to_string(template, context)

    def html(self, template, context):
        self._html = self._render(template, context)

    def text(self, template, context):
        self._text = self._render(template, context)

    def subject(self, template, context):
        self._subject = self._render(template, context)

    def _log_in_messages(self, message, subject):
        try:
            from core.models.message import Messages, MessageUser
            new_message = Messages.objects.create(
                message_type=Messages.MESSAGE_TYPE_EMAIL,
                message=message,
                subject=subject,
                message_send_level=Messages.MESSAGE_SEND_LEVEL_SPECIFIC,
                direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER,
                booking_id=self.analytic_info.get('booking_id'),
                action=self.analytic_info.get('action'),
                notification_id=self.analytic_info.get('notification_id'),
                sent_by_id=self.analytic_info.get('sent_by_id'),
                label=self.analytic_info.get('label'),
            )
            sent_to_list = self.to + self.cc_list

            for item in sent_to_list:
                message_user = MessageUser.objects.create(
                    user_id=self.analytic_info.get('sent_for_account_id'),
                    message=new_message,
                    sent_to=item,
                    delivery_report='pending',
                )
        except:
            log.exception('Failed to add email entry in messages database.')

    def send(self, template_folder_name=None, email_body=None, subject=None, fail_silently=False, attachments=[]):
        if not template_folder_name and not email_body:
            raise Exception('Invalid Email. Either select template or provide email_body')

        if not self.from_email:
            self.from_email = settings.DEFAULT_FROM_EMAIL

        if template_folder_name:
            html_template, subject_text, text_template = self._build_template_path(template_folder_name)
            self.html(template=html_template, context=self.context)
            self.text(template=text_template, context=self.context)
            self.subject(template=subject_text, context=self.context)
            if subject:
                self._subject = subject

            if settings.SMS_PROVIDER == 'MANDRILL':
                EmailService.send_mail_using_mandrill_without_template(
                    subject=self._subject,
                    body=self._html,
                    to_email_list=self.to,
                    from_email=self.from_email,
                    from_name=self.from_name,
                    attachments=attachments,
                    cc_email_list=self.cc_list)
            else:
                msg = EmailMultiAlternatives(
                    self._subject,
                    self._text,
                    self.from_email,
                    self.to,
                    cc=self.cc_list if len(self.cc_list)>0 else None
                )
                if self._html:
                    msg.attach_alternative(self._html, 'text/html')

                msg.send(fail_silently)
            self._log_in_messages(message=self._html, subject=self._subject)
        else:
            formatted_body = email_body % self.context
            formatted_subject = subject % self.context
            if settings.SMS_PROVIDER == 'MANDRILL':
                EmailService.send_mail_using_mandrill_without_template(formatted_subject, self.to,
                                                                                formatted_body,
                                                                                cc_email_list=self.cc_list,
                                                                                attachments=attachments,
                                                                                from_email=self.from_email,
                                                                                from_name=self.from_name,
                                                                       )
            else:
                EmailService.send_email(formatted_subject, formatted_body, self.to, cc_address_list=self.cc_list,
                                        email_format=self.email_format)
            self._log_in_messages(message=formatted_body, subject=formatted_subject)
