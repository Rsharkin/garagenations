__author__ = 'inderjeet'

from rest_framework import viewsets, generics
from api.api_views.custom_mixins import LoggingMixin
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import status
from core.models.users import UserInquiry, BumperUser
from core.models.master import Source
import requests
import logging
logger = logging.getLogger(__name__)


def create_new_fb_inquiry(user, form_name):
    return UserInquiry.objects.create(user=user,
                                              inquiry='Marketing lead. Please call and inquire.',
                                              status=UserInquiry.INQUIRY_OPEN,
                                              source=Source.objects.get(source='fb_lead_form'),
                                              city_id=1,
                                              utm_source='fb_lead_form',
                                              utm_medium='cpc',
                                              utm_campaign=form_name,
                                      )


class FacebookLeadViewSet(LoggingMixin, viewsets.GenericViewSet):
    """
        Endpoint for webhook for facebook lead form.
    """
    permission_classes = ()

    @list_route(methods=['post', 'get'])
    def facebook_lead_form(self, request):
        logger.debug('--------------- API_Webhook_FB_LeadGen request data=%s' % str(request.data))
        fb_long_token = 'EAAEsZBm9K2fABAMdgfZAG231kiscAyvTKoTMLAC9pKZA2fWIq0alJM5FnDW5M5KvROEidxHaF7s7c7ZC1dehFdBZBN3NogWEMZCmrE6NL9RWoXrS6ugsuoI3ZCfXdXJqEdqoCu42NPKj8pJjqBZChpFUIErZCOeLpEfGL54QiA9JixQZDZD'
        """
            {u'entry': [{u'changes': [{u'field': u'leadgen', u'value': {u'created_time': 1503325264, u'page_id': u'448498065318454'
            , u'form_id': u'217925195403806', u'leadgen_id': u'224445114751814'}}], u'id': u'448498065318454'
            , u'time': 1503325265}], u'object': u'page'}
        """
        if 'entry' in request.data:
            for entry in request.data.get('entry'):
                for change in entry.get('changes'):
                    if change.get('field') == 'leadgen':
                        # then get details of the lead.
                        response = requests.get("https://graph.facebook.com/v2.10/%s?access_token=%s" % (change.get('value').get('leadgen_id'),fb_long_token))
                        logger.debug('--------------- API_Webhook_FB_LeadGen Response for lead details=%s, %s' % (response.status_code,str(response.json())))
                        """
                            {u'created_time': u'2017-08-21T14:53:58+0000', u'field_data': 
                            [{u'values': [u'inderjeetrao.ir@gmail.com'], u'name': u'email'}, 
                            {u'values': [u'Inderjeet Rao'], u'name': u'full_name'}, 
                            {u'values': [u'+918800165656'], u'name': u'phone_number'}], 
                            u'id': u'730193697181458'}
                        """
                        if response.status_code == 200:
                            form_response = requests.get("https://graph.facebook.com/v2.10/%s?access_token=%s" % (
                            change.get('value').get('form_id'), fb_long_token))

                            logger.debug('--------------- API_Webhook_FB_LeadGen Response for form details=%s, %s' % (
                                form_response.status_code, str(form_response.json())))

                            form_name = 'fb_form_name_not_found'
                            if form_response.status_code == 200:
                                form_name = form_response.json().get('name')

                            lead_data = {}
                            for field in response.json().get('field_data'):
                                if field.get('name') == 'email':
                                    lead_data['email'] = field.get('values')[0]
                                elif field.get('name') == 'full_name':
                                    lead_data['full_name'] = field.get('values')[0]
                                elif field.get('name') == 'phone_number':
                                    lead_data['phone_number'] = field.get('values')[0]
                                    if str(lead_data['phone_number']).startswith('+91'):
                                        lead_data['phone_number'] = lead_data['phone_number'][3:]

                            # check if user exists with this phone number:
                            bumper_user = BumperUser.objects.filter(phone=lead_data.get('phone_number'))
                            if bumper_user.exists():
                                # user found create inquiry
                                logger.debug('--------------- API_Webhook_FB_LeadGen Found existing user %s' % bumper_user.first().id)
                                user_inquiry = create_new_fb_inquiry(bumper_user.first(), form_name)
                            else:
                                # create user and then create inquiry
                                user = BumperUser.objects.create_user(name=lead_data['full_name'],
                                                                      email=lead_data['email'],
                                                                      phone=lead_data['phone_number'], city_id=1,
                                                                      source=Source.objects.get(source='fb_lead_form'),
                                                                      utm_source='fb_lead_form',
                                                                      utm_medium='cpc',
                                                                      utm_campaign=form_name)
                                logger.debug('--------------- API_Webhook_FB_LeadGen New user created %s' % user.id)
                                user_inquiry = create_new_fb_inquiry(user, form_name)

                            logger.debug('--------------- API_Webhook_FB_LeadGen New Inquiry Created: %s' % user_inquiry.id)
                        else:
                            logger.error('--------------- API_Webhook_FB_LeadGen Failed to retrieve Lead data')

        return Response(status=status.HTTP_200_OK, data=int(request.REQUEST.get('hub.challenge', 0)))
