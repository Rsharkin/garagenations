from django import forms
import re
from core.models.users import BumperUser, UserCar
from core.models.booking import Booking
from core.constants import GROUP_OPS_USER
from passwords.validators import (
    DictionaryValidator, LengthValidator, ComplexityValidator)

PHONE_NUMBER_REGEX = re.compile(r'^[+]?((\d+[\s]?[-]?\d+)+)$')
WIDGET_ATTRS_TEXT = {"class":"text-input small-input"}


class PhoneNumberField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        kwargs['regex'] = PHONE_NUMBER_REGEX
        kwargs['max_length'] = 10
        kwargs['min_length'] = 10
        kwargs['widget'] = forms.TextInput(attrs=WIDGET_ATTRS_TEXT)
        kwargs['error_messages'] = {
            'invalid' : "Invalid phone Number",
            'required': "Phone Number field is required"
        }
        super(PhoneNumberField, self).__init__(*args, **kwargs)


class PhoneNumberForm(forms.Form):
    phone = PhoneNumberField(required=True)


class ForgotPasswordForm(forms.Form):
    username = PhoneNumberField(max_length=10)

    def clean(self):
        username = self.cleaned_data.get('username')
        user = BumperUser.objects.filter(ops_phone=username).first()
        if not user:
            raise forms.ValidationError('You are not user of Bumper.')
        elif not user.is_active:
            raise forms.ValidationError('Your Account has been disabled.')
        elif not user.groups.filter(name=GROUP_OPS_USER).exists():
            raise forms.ValidationError('You are not user of Bumper.')
        return username


class ChangePasswordForm(forms.Form):
    password = forms.CharField(validators=[
        DictionaryValidator(words=['Bumper','bumper', 'autoninja', 'Autoninja','unbox','Unbox','bumper@123','bumper123',
                                   'bumper@1234','bumper@312','bumper321','bumper4321','0987654321','12345678',
                                   '87654321'], threshold=0.9),
        LengthValidator(min_length=8, max_length=25),
        ComplexityValidator(complexities=dict(
            WORDS=1,
            UPPER=1,
        )),
    ])
    confirm_password = forms.CharField(min_length=8, max_length=25)

    def clean_confirm_password(self):
        # self mobile number
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            raise forms.ValidationError('Password and Confirm Password does not match.')

        return confirm_password


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ('updated_at','created_at')

    def __init__(self, *args, **kwargs):
        super(BookingAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['user'].queryset = BumperUser.objects.filter(id=self.instance.user_id)
            self.fields['usercar'].queryset = UserCar.objects.filter(id=self.instance.usercar_id)
