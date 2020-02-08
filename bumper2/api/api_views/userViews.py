__author__ = 'anuj'

from django.contrib.auth import get_user_model, authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When, F, DecimalField, Sum, Count
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from social.apps.django_app.utils import load_backend
from social.apps.django_app.utils import load_strategy
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.exceptions import AuthAlreadyAssociated

from api.permissions import (UserIsOwnerOrAdminOrPost, IsOwnerOrAdmin, IsPostOrAdmin,
                             IsAdminUser, IsDriver, IsWorkshopExecutive, IsScratchFinder, PermissionOneOf)
from api.serializers import userSerializer
from api.serializers import masterSerializers
from api.custom_paginations import PaginationWithCreditSum

from core.managers import userManager, bookingManager
from core.models.users import (
    UserCar, UserAddress, PartnerLead, UserInquiry, WorkshopUser, DriverLocation, UserAttendance,
    ScratchFinderLead, CreditTransaction
)
from core.models.booking import Booking, UserVendorCash
from core.models.master import CancellationReasons, Source
from core.models.referral import ReferralCode, ReferralCampaign
from services.cognito_based_login import get_aws_open_id_token

from api.custom_filters import UserFilter
from api.api_views.custom_mixins import LoggingMixin

import logging
logger = logging.getLogger(__name__)


class UserCarViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin, )
    queryset = UserCar.objects.filter(active=True)
    serializer_class = userSerializer.UserCarSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'active')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        return userManager.get_usercar_queryset(self.request.user)

    def perform_create(self, serializer):
        vdata = serializer.validated_data
        user = self.request.user
        if vdata.get('user') and self.request.user.groups.filter(name='OpsUser').exists():
            user = vdata.get('user')
        input_car_model = vdata.get('car_model')
        year = vdata.get('year')
        if year and input_car_model:
            input_car_model = input_car_model.get_car_model_by_year(year)
        serializer.save(user=user, car_model=input_car_model, active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        other_usercar_count = UserCar.objects.filter(user=user, active=True).exclude(id=instance.id).count()
        if other_usercar_count > 0:
            bookings = Booking.objects.filter(usercar=instance)
            open_bookings = bookingManager.filter_open_booking(bookings)
            if open_bookings:
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                instance.active = False
                instance.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_409_CONFLICT)


class UserViewSet(LoggingMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (UserIsOwnerOrAdminOrPost,)
    queryset = get_user_model().objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = UserFilter
    serializer_class = userSerializer.UserSerializer

    def get_serializer_context(self):
        context = super(UserViewSet, self).get_serializer_context()
        context['is_admin'] = self.request.user.groups.filter(name='OpsUser').exists()
        return context

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        User = get_user_model()
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(id=self.request.user.id)
        return queryset.select_related('city').prefetch_related('groups','user_credit', 'user_detail')

    def create(self, request, *args, **kwargs):
        return self.social_signup(request)

    def social_signup(self, request, pk=None):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """

        provider = request.data.get('provider')

        if provider == 'skip':
            # TODO: create skip and none also as backend
            if request.user and not request.user.is_anonymous():
                user = request.user
            else:
                data = dict(request.data)
                if not data.get('source') and request.META.get('HTTP_SOURCE'):
                    data['source'] = Source.objects.filter(source=self.request.META.get('HTTP_SOURCE')).first()
                user = userManager.create_user(data)
            if user:
                token = user.get_drf_token()
                result = {'token': token.key, 'user': userSerializer.UserSerializer(user,
                                                                                    remove_fields=['referral',
                                                                                                   'active_devices']).data}
                response = Response(result, status=status.HTTP_201_CREATED)
            else:
                response = Response(status=status.HTTP_403_FORBIDDEN)
            return response

        # If this request was made with an authenticated user, try to associate this social
        # account with it
        authed_user = request.user if not request.user.is_anonymous() else None

        # `strategy` is a python-social-auth concept referencing the Python framework to
        # be used (Django, Flask, etc.). By passing `request` to `load_strategy`, PSA
        # knows to use the Django strategy
        strategy = load_strategy(request)
        # Now we get the backend that corresponds to our user's social auth provider
        # e.g., Facebook, Twitter, etc.
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

        token = None

        if isinstance(backend, BaseOAuth1):
            # Twitter, for example, uses OAuth1 and requires that you also pass
            # an `oauth_token_secret` with your authentication request
            token = {
                'oauth_token': request.data.get('access_token'),
                'oauth_token_secret': request.data.get('access_token_secret'),
            }
        elif isinstance(backend, BaseOAuth2):
            # We're using oauth's implicit grant type (usually used for web and mobile
            # applications), so all we have to pass here is an access_token
            token = request.data.get('access_token')

        try:
            # if `authed_user` is None, python-social-auth will make a new user,
            # else this social account will be associated with the user you pass in
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            # You can't associate a social account with more than user
            return Response({"errors": "That social media account is already in use"},
                            status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.exception("Exception in social signup:%s" % provider)
            return Response({"errors": "Some problem in signing up"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if user and user.is_active:
            # if the access token was set to an empty string, then save the access token
            # from the request
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                # Facebook for example will return the access_token in its response to you.
                # This access_token is then saved for your future use. However, others
                # e.g., Instagram do not respond with the access_token that you just
                # provided. We save it here so it can be used to make subsequent calls.
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            #return jwt_token and user id
            jwt_token = user.get_jwt_token()
            result = {
                'token': jwt_token,
                'user': userSerializer.UserSerializer(user).data
            }
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": "Error with social authentication"},
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def send_signup_code(self, request):
        """
        Send signup code when user signs up.

        responseMessages:
            - code: 400
              message: 'Different User already exists with this phone. Please login to that.'
            - code: 500
              message: 'SMS sending/ OTP processing failed.'
            - code: 400
              message: 'User already exists. Please login.'
            - code: 400
              message: Input errors.
        """
        serializer = userSerializer.SendAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.user
            if data.get('is_scratch_finder'):
                data['group_name'] = "ScratchFinder"
            if not user.is_anonymous():
                if user.phone != data.get('phone'):
                    exists_user_by_phone = userManager.find_matching_users_by_phone(data.get('phone'))
                    if exists_user_by_phone and not exists_user_by_phone.is_active:
                        return Response(
                            {
                                'status': 'Different User already exists with this phone but is inactive. '
                                          'Please contact Bumper customer care.'
                            },
                            status=status.HTTP_400_BAD_REQUEST)
                    if exists_user_by_phone and exists_user_by_phone != user:
                        if exists_user_by_phone.is_otp_validated:
                            return Response({
                                'status': 'Different User already exists with this phone. Please login to that.'},
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            user = exists_user_by_phone

                # TODO check whether this is correct in overall process. ie replacing the number if already exists.
                create_rc = False  # Do we need to create referral code or not
                if not user.phone or user.phone != data.get('phone'):
                    user.phone = data.get('phone')
                    create_rc = True

                user.name = data.get('name')
                user.email = data.get('email')
                if data.get('city'):
                    user.city = data.get('city')
                user.save()
                # create user device
                user.save_user_device(data)
                if create_rc:
                    user.create_referral_code()
                    userManager.handle_referral_code(user, data)

                if user.send_auth_code(user.phone):
                    return Response({"user_id": user.id, 'status': 'OTP Sent'})
                else:
                    return Response({'status': 'SMS sending/ OTP processing failed.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                # Check for existing User
                #only phone number
                matching_user = userManager.find_matching_users_by_phone(data.get('phone'))
                if matching_user:
                    # check if user exists with email or phone
                    #if matching_user.email == data.get('email') and not matching_user.phone:
                    if not matching_user.is_otp_validated:
                        # if not phone number then just update number and move ahead.
                        matching_user.phone = data.get('phone')
                        matching_user.name = data.get('name')
                        matching_user.email = data.get('email')
                        if data.get('city'):
                            matching_user.city = data.get('city')
                        matching_user.save()
                        user = matching_user
                    else:
                        return Response({'status':'User already exists. Please login.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Create user if not there
                    data.update({'city_id': data.get('city').id if data.get('city') else None})
                    source_str = data.get('source') or self.request.META.get('HTTP_SOURCE')
                    source = Source.objects.filter(source=source_str).first()
                    data.update({'source': source})
                    user = userManager.create_user(data)
                    userManager.handle_referral_code(user, data)

                # create user device
                user.save_user_device(data)

                # Send OTP
                if user.send_auth_code(user.phone):
                    # return Response({'token': token.key, 'status': 'OTP Sent'}, status=status.HTTP_200_OK)
                    return Response({'status': 'OTP Sent'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': 'SMS sending/ OTP processing failed.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def validate_auth_code(self, request):
        """
            validate auth code.
        """
        new_user = request.user
        serializer = userSerializer.ValidateAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            existing_user = userManager.find_matching_users_by_phone(data.get('phone'))
            if existing_user and existing_user.is_active:
                if existing_user.validate_auth_code(data.get('auth_code')):
                    if not new_user.is_anonymous() and existing_user != new_user:
                        userManager.merge_new_user_to_existing(existing_user, new_user)
                    if existing_user.email and not existing_user.is_email_verified:
                        existing_user.send_verification_email(request)
                    # If there is event code - add incentive
                    if data.get('event_code'):
                        event_code = data.get('event_code')
                        incentive_data = {"name": event_code,
                                          "entity": UserVendorCash.ENTITY_USER,
                                          "entity_id": existing_user.id,
                                          "promise_info": "Remarketing for login/signup",
                                          "user": existing_user,
                                          "promise_and_transfer": True}
                        userManager.handle_incentive_events(incentive_data)
                    return Response({'token': existing_user.get_jwt_token(),
                                     'user': userSerializer.UserSerializer(existing_user,
                                                                           remove_fields=['referral']).data,
                                     'status': 'OTP is Valid'})
                else:
                    return Response({'status': 'OTP is In-correct.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': "User account is disabled."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def send_login_code(self, request):
        serializer = userSerializer.PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = userManager.find_matching_users_by_phone(data.get('phone'))
            if not user or not user.is_active:
                return Response({'status': 'No User with this Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
            # if not user.is_otp_validated:
            #     return Response({'status': 'No User with this Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
            if user.send_auth_code(user.phone, send_email=True):
                if data.get('is_scratch_finder'):
                    if not user.groups.filter(name='ScratchFinder').exists():
                        g = Group.objects.filter(name='ScratchFinder').first()
                        if g:
                            g.user_set.add(user)
                return Response({'status': 'OTP Sent'})
            else:
                return Response({'status': 'SMS sending/ OTP processing failed.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def resend_otp(self, request):
        """
        Resend OTP if user has already tried once.

        responseMessages:
            - code: 400
              message: 'No User with this Phone Number'
            - code: 500
              message: 'SMS sending/ OTP processing failed.'
            - code: 200
              message: 'OTP Sent'
            - code: 400
              message: Input errors.

        """
        serializer = userSerializer.PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = userManager.find_matching_users_by_phone(data.get('phone'))

            if not user or not user.is_active:
                return Response({'status': 'No User with this Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
            if user.send_auth_code(user.phone):
                return Response({'status': 'OTP Sent'})
            else:
                return Response({'status': 'SMS sending/ OTP processing failed.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def get_user_profile_with_token(self, request, pk):
        """
            get user profile with token. Used in ops panel.
        """
        user = self.get_object()
        return Response({'token': user.get_jwt_token(), 'user': userSerializer.UserSerializer(user).data,
                         'permissions': user.get_all_permissions()})

    @list_route(methods=['post'])
    def send_reg_details(self, request):
        """
        Resend OTP if user has already tried once.

        responseMessages:
            - code: 400
              message: 'Registration details cannot be saved for anonymous user.'
            - code: 200
              message: 'Token saved successfully'
            - code: 400
              message: Input errors.
        """
        serializer = userSerializer.SavePushRegSerializer(data=request.data)
        utm_serializer = userSerializer.UTMFieldSerializer(data=request.data)
        if serializer.is_valid() and utm_serializer.is_valid():
            data = serializer.validated_data
            user = request.user

            if user.is_anonymous():
                return Response({'status': 'Registration details cannot be saved for anonymous user.'}, status=status.HTTP_400_BAD_REQUEST)

            user.save_user_device(data)
            utm_data = utm_serializer.validated_data
            user.save_user_fields(utm_data)

            return Response("Token saved successfully.", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def verify_email(self, request):
        """
            Verify user's email.
        """
        user = request.user
        if user.email and not user.is_email_verified:
            user.send_verification_email(request)
        return Response({"status": "Verification Email sent"})

    @list_route(methods=['post'], url_path='create-user')
    def create_user_from_ops(self, request):
        """
            Create User from Ops (for web signups and iOS users) or some exception cases
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            serializer = userSerializer.UserSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                existing_user = None
                if data.get('phone'):
                    existing_user = userManager.find_matching_users_by_phone(data.get('phone'))
                if existing_user:
                    if existing_user.is_otp_validated:
                        return Response({'status': 'User already exists. Please login.',
                                         'user': userSerializer.UserSerializer(existing_user).data},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'status': 'User already exists. OTP not validated. Please signup.',
                                         'user': userSerializer.UserSerializer(existing_user).data},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    data.update({'city_id': data.get('city').id if data.get('city') else None})
                    user = userManager.create_user(data)
                    return Response({'status': 'User Created',
                                     'user': userSerializer.UserSerializer(user).data},
                                    status=status.HTTP_200_OK)
            else:
                if serializer.errors.has_key('phone'):
                    existing_user = userManager.find_matching_users_by_phone(request.data.get('phone'))
                    if existing_user:
                        return Response({"errors": serializer.errors,
                                         "user": userSerializer.UserSerializer(existing_user).data},
                                        status=status.HTTP_409_CONFLICT)
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Not Found"}, status=status.HTTP_403_FORBIDDEN)

    @list_route(methods=['post'])
    def login_with_password(self, request):
        """
            Login users with password - will be used mainly for internal apps - driver, workshop manager etc.
        """
        serializer = userSerializer.AuthSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = authenticate(username=data.get('username'),password=data.get('password'))
            if user is not None and user.is_active:
                # user is verified
                return Response({'token': user.get_jwt_token(), 'user': userSerializer.UserSerializer(user).data})
            else:
                # the authentication system was unable to verify the username and password
                return Response({"detail": "Wrong username/password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def sync_user_details(self, request):
        """
            Get user details:
            1. mandatory version code
        """
        user = self.request.user

        # usercar_queryset = userManager.get_usercar_queryset(self.request.user)
        # serializer = UserCarSerializer(usercar_queryset, many=True)
        # usercar_data = serializer.data
        usercar_view = UserCarViewSet.as_view({'get': 'list'})
        usercar_data = usercar_view(request)
        cancellation_reasons = CancellationReasons.objects.filter(
                reason_owner=CancellationReasons.REASON_OWNER_CUSTOMER,
                active=True).order_by('order_num')
        from django.conf import settings
        return Response({
            'update_ver_code':{
                "ANDROID": settings.ANDROID_VERSION_CODE,
                "iPhone": settings.IPHONE_VERSION_CODE,
            },
            "bill_upload_campaign": getattr(settings, 'BILL_UPLOAD_CAMPAIGN', False),
            "usercar_list": usercar_data.data.get('results'),
            "cancellation_reasons": masterSerializers.CancellationReasonsSerializer(cancellation_reasons,many=True,
                                                                                    new_fields=['reason','id']).data,
        }, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def delete_testing_user(self, request):
        phone = request.data.get('phone', '9740176267')
        if phone in ['9740176267', '9886452736']:
            user = userManager.find_matching_users_by_phone(phone)
            if user:
                user.phone = None
                user.is_active = False
                user.save()
                return Response({'message': 'User deleted from system'})
        return Response({'message': 'No user with testing phone number.'})

    @list_route(methods=['get'], url_path='call-screen')
    def call_screen(self, request):
        user = request.user
        booking = None
        if user.is_anonymous():
            user = None
        else:
            bookings = bookingManager.filter_open_booking(Booking.objects.filter(user=user).order_by('-created_at'))
            booking = bookings.first()
        return Response({"data": bookingManager.get_call_screen_dict(booking=booking, user=user)})

    @list_route(methods=['post'])
    def cancel_booking_followup(self, request):
        user = request.user
        booking = Booking.objects.filter(user=user).order_by('-updated_at').first()
        if booking and booking.status_id == 24:
            serializer = userSerializer.CancelledBookingFollowupSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                data['updated_by'] = user
                bookingManager.update_followup(booking, data)
                return Response({"detail": "Followup Created"})
            else:
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "No Followup Created"})


class UserAddressViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin,)
    queryset = UserAddress.objects.all()
    serializer_class = userSerializer.UserAddressSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user',)

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = UserAddress.objects.all()
        else:
            queryset = UserAddress.objects.filter(user=self.request.user)

        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def perform_create(self, serializer):
        vdata = serializer.validated_data
        user = self.request.user
        if vdata.get('user') and self.request.user.groups.filter(name='OpsUser').exists():
            user = vdata.get('user')
        serializer.save(user=user)


class PartnerLeadViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking discount to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsPostOrAdmin,)
    queryset = PartnerLead.objects.all()
    serializer_class = userSerializer.PartnerLeadSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('mobile',)


class UserInquiryViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin, )
    queryset = UserInquiry.objects.all()
    serializer_class = userSerializer.UserInquirySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'status')

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'followup':
            serializer_class = userSerializer.UserInquiryFollowupSerializer
        return serializer_class

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = UserInquiry.objects.all()
        else:
            queryset = UserInquiry.objects.filter(user=self.request.user)
        if self.action == 'followup' and self.request.method == 'GET':
            queryset = self.get_serializer_class().setup_eager_loading(queryset)

        return queryset.select_related('user', 'car_model__brand')

    def perform_create(self, serializer):
        vdata = serializer.validated_data
        user = self.request.user
        if vdata.get('user') and self.request.user.groups.filter(name='OpsUser').exists():
            user = vdata.get('user')
        if not vdata.get('source') and self.request.META.get('HTTP_SOURCE'):
            vdata['source'] = Source.objects.filter(source=self.request.META.get('HTTP_SOURCE')).first()
        serializer.save(user=user, updated_by=self.request.user)

    @detail_route(methods=['get','patch'], permission_classes=[IsAdminUser])
    def followup(self, request, pk=None):
        """
            This API will give booking cart details
        """
        if request.method == 'PATCH':
            return super(UserInquiryViewSet, self).partial_update(request)
        else:
            return super(UserInquiryViewSet, self).retrieve(request)

    @list_route(methods=['post'], permission_classes=[], url_path='chat-inquiry')
    def chat_inquiry(self, request):
        """
            Create User Inquiry from Chat - This has to be done without authentication.
        """
        user_inquiry_serializer = userSerializer.UserInquirySerializer(data=request.data)
        user_detail_serializer = userSerializer.ChatUserSerializer(data=request.data)
        if user_inquiry_serializer.is_valid() and user_detail_serializer.is_valid():
            inquiry_data = user_inquiry_serializer.validated_data
            user = None
            if not inquiry_data.get('user'):
                user_detail = user_detail_serializer.validated_data
                if not user_detail.get('phone') and not user_detail.get('email'):
                    # send email to our team about this chat
                    logger.error('No phone and email for this chat inquiry: %s', inquiry_data)
                    return Response({'detail': 'No phone and email for this chat inquiry'})
                else:
                    user = None
                    if user_detail.get('phone'):
                        user = userManager.find_matching_users_by_phone(user_detail.get('phone'))
                    if not user:
                        if request.META.get('HTTP_SOURCE'):
                            user_detail['source'] = Source.objects.filter(source=self.request.META.get('HTTP_SOURCE')).first()
                        user_detail.update({'city_id': inquiry_data.get('city').id if inquiry_data.get('city') else None})
                        user = userManager.create_user(user_detail)

            user_inquiry_serializer.save(user=user)
            return Response({"detail": "Chat Inquiry Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": user_inquiry_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MarketingCampaignSet(LoggingMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication, SessionAuthentication)
    serializer_class = userSerializer.MarketingCampaignSerializer

    @list_route(methods=['post'])
    def bill_upload(self, request):
        serializer = userSerializer.MarketingCampaignSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            from core.models.master import Notifications
            import base64

            notices = Notifications.objects.filter(name='OPS_MARKETING_BILL_UPLOAD')
            for notice in notices:
                if notice.type == Notifications.NOTIFICATION_TYPE_EMAIL:
                    context = {
                        'name': data.get('name'),
                        'email': data.get('email'),
                        'mobile': data.get('phone'),
                        'message': 'PFA Bill Uploaded By User.',
                        'utm_source': data.get('utm_source'),
                        'utm_medium': data.get('utm_medium'),
                        'utm_campaign': data.get('utm_campaign')
                    }
                    body = notice.template % context
                    subject = notice.subject % context
                    logger.debug('Send Email for Bill upload id=%s' % context)
                    attachment = {
                        'content': base64.b64encode( data.get('media').read()),
                        'name': 'uploaded_bill',
                        'type': 'image/jpeg'
                    }
                    from services.email_service import EmailService
                    EmailService.send_mail_using_mandrill_without_template(
                        subject,
                        notice.get_to_list(),
                        body,
                        cc_email_list=notice.get_cc_list(),
                        attachments=[attachment])

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class WorkshopUserViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = WorkshopUser.objects.all()
    serializer_class = userSerializer.WorkshopUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'workshop')

    def get_queryset(self):
        """
        Filter objects so a user (workshop executive) only sees his own stuff.
        If user is workshop manager, let him see all.
        """
        queryset = WorkshopUser.objects.filter(user=self.request.user)
        return queryset.select_related('user','workshop')


class DriverLocationViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows create/update/list booking location for driver
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsDriver, IsAdminUser)
    queryset = DriverLocation.objects.all()
    serializer_class = userSerializer.DriverLocationSerializer


class UserAttendanceViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows create/update/list booking location for driver
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (PermissionOneOf,)
    permissions_list = [IsWorkshopExecutive, IsAdminUser]
    queryset = UserAttendance.objects.all()
    serializer_class = userSerializer.UserAttendanceSerializer

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = UserAttendance.objects.all()
        else:
            queryset = UserAttendance.objects.filter(user=self.request.user)
        return queryset


class APICognitoView(LoggingMixin, APIView):
    """
        GET IdentityId/Token that can be used by client to get Temporary AWS credentials
        based on our authentication.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsDriver, IsWorkshopExecutive, IsAdminUser)

    def get(self, request):
        """
            get updated IdentityID and Token from AWS Cognito
        :param request:
        :return:
        """

        data_dic = {}
        # keeping user.username instead of ops_phone.
        resp = get_aws_open_id_token(request.user.username)
        if resp:
            status_from_aws = resp['ResponseMetadata']['HTTPStatusCode']
            data_dic['identity_id'] = resp['IdentityId']
            data_dic['token'] = resp['Token']
        else:
            logger.exception('Something wrong with Cognito call')
            status_from_aws = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data_dic, status=status_from_aws)


class ScratchFinderLeadViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
       API endpoint that allows create/update/list scratch finder leads
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (PermissionOneOf,)
    permissions_list = [IsScratchFinder, IsAdminUser]
    queryset = ScratchFinderLead.objects.all()
    serializer_class = userSerializer.ScratchFinderLeadSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'status')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = ScratchFinderLead.objects.all()
        else:
            queryset = ScratchFinderLead.objects.filter(user=self.request.user)
        queryset = queryset.select_related('car_model__brand')
        return queryset


class UserAccountSummary(LoggingMixin, APIView):
    """
        GET user's account summary
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (PermissionOneOf,)
    permissions_list = [IsScratchFinder, IsAdminUser]

    def get(self, request):
        output = UserVendorCash.objects.filter(user=request.user).aggregate(
                    alloted_cash=Sum(Case(
                        When(transferred=False, then=F('amount')),
                        output_field=DecimalField(),
                    )),
                    earned_cash=Sum(Case(
                        When(transferred=True, then=F('amount')),
                        output_field=DecimalField(),
                    )))
        # may need to optimize with join/extra if there are many leads submitted.
        sfleads_phone = ScratchFinderLead.objects.filter(user=request.user).values_list('phone')
        num_cars_picked_up = Booking.objects.filter(user__phone__in=sfleads_phone,
                                                    status__flow_order_num__range=(9,24)).count()

        status_counts = ScratchFinderLead.objects.filter(
                                            user=request.user).values('status').annotate(count=Count('status'))

        output["status_counts"] = status_counts
        output["converted"] = num_cars_picked_up
        return Response(output, status=status.HTTP_200_OK)


class ReferralCodeViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows create/update/list booking location for driver
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin, )
    queryset = ReferralCode.objects.all()
    serializer_class = userSerializer.ReferralCodeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'code')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = ReferralCode.objects.all()
        else:
            queryset = ReferralCode.objects.filter(user=self.request.user)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super(ReferralCodeViewSet, self).list(request, args, kwargs)
        # Add Referral campaign data.
        rc = ReferralCampaign.objects.filter(active=True, name="CREATE_USER").first()
        if rc:
            response.data['campaign'] = userSerializer.ReferralCampaignSerializer(rc,
                                                                                  new_fields=['description',
                                                                                              'terms',
                                                                                              'share_message',
                                                                                              'share_title']).data
        return response


class CreditTransactionViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows create/update/list booking location for driver
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin, )
    queryset = CreditTransaction.objects.all()
    pagination_class = PaginationWithCreditSum
    serializer_class = userSerializer.CreditTransactionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user', 'trans_type')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = CreditTransaction.objects.all()
        else:
            queryset = CreditTransaction.objects.filter(user=self.request.user)

        return queryset
