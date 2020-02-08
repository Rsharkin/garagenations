import random
import string

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from multiselectfield import MultiSelectField

from core.models.common import CreatedAtAbstractBase
from core.models.users import BumperUser
from core.models.master import City, Package


class CouponManager(models.Manager):
    def create_coupon(self, type, value, applicable_to, user=None, valid_until=None, prefix="", campaign=None,
                      booking_type=None,max_use=0,used_times=0,
                      amount_limit=None,cashback_value=0,cashback_type=None,cashback_amt_limit=None,desc="",title="."):
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix),
            type=type,
            desc=desc,
            user=user,
            valid_until=valid_until,
            campaign=campaign,
            booking_type=booking_type,
            applicable_to=applicable_to,
            max_use=max_use,
            used_times=used_times,
            amount_limit=amount_limit,
            cashback_value=cashback_value,
            cashback_type=cashback_type,
            cashback_amt_limit=cashback_amt_limit,
            title=title,
            is_cashback=True
        )
        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            return Coupon.objects.create_coupon(type, value, user, valid_until, prefix, campaign,
                                                booking_type, applicable_to,max_use,used_times,amount_limit,cashback_value,
                                                cashback_type,cashback_amt_limit,desc,title)
        else:
            return coupon

    def create_coupons(self, quantity, type, value, applicable_to, valid_until=None, prefix="",campaign=None,
                       booking_type=None,max_use=0,used_times=0,
                       amount_limit=None,cashback_value=0,cashback_type=None,cashback_amt_limit=None,desc="",title="."):
        coupons = []
        for i in range(quantity):
            coupons.append(self.create_coupon(type, value, applicable_to, None, valid_until, prefix,campaign,
                                              booking_type,max_use,used_times,amount_limit,
                                              cashback_value,cashback_type,cashback_amt_limit,desc,title))
        return coupons


@python_2_unicode_compatible
class Coupon(CreatedAtAbstractBase):
    COUPON_TYPE_MONETORY = 'monetary'
    COUPON_TYPE_PERCENTAGE = 'percentage'

    COUPON_TYPES = (
        (COUPON_TYPE_MONETORY, 'Money based coupon'),
        (COUPON_TYPE_PERCENTAGE, 'Percentage discount'),
    )

    COUPON_APPLICATION_PART = 1
    COUPON_APPLICATION_MATERIAL = 2
    COUPON_APPLICATION_LABOUR = 3


    COUPON_APPLICATION_TYPES = (
        (COUPON_APPLICATION_PART, 'Applicable to Part price'),
        (COUPON_APPLICATION_MATERIAL,'Applicable to Material price'),
        (COUPON_APPLICATION_LABOUR,'Applicable to Labour price'),
    )
    CODE_LENGTH = 9
    CODE_CHARS = string.ascii_uppercase+string.digits

    value = models.IntegerField(_("Value"), help_text=_("Arbitrary coupon value"))
    amount_limit = models.IntegerField(_("Limit"),
                                       help_text=_("For Percentage discount, this is the amount limit for which coupon can be used"),
                                       blank=True,null=True)
    code = models.CharField(_("Code"), max_length=30, unique=True, blank=True,db_index=True,
                            help_text=_("Leaving this field empty will generate a random code."))
    desc = models.CharField(_("Description"),max_length=255)
    type = models.CharField(_("Type"), max_length=20, choices=COUPON_TYPES)
    user = models.ForeignKey(BumperUser, verbose_name=_("User"), null=True, blank=True,
        help_text=_("You may specify a user you want to restrict this coupon to."))
    valid_until = models.DateTimeField(_("Valid until"), blank=True, null=True,
        help_text=_("Leave empty for coupons that never expire"))
    applicable_to = MultiSelectField(_("Applicable To"),max_length=20, choices=COUPON_APPLICATION_TYPES)
    used_times = models.IntegerField(_("Used Times"), default=0,
                                     help_text=_("How many times this coupon can be used PER USER? 0 means infinite times"))
    max_use = models.IntegerField(_("Max Use"),default=0,
                                  help_text=_("How many times this coupon can be used? 0 means infinite times"))
    campaign = models.ForeignKey('Campaign', verbose_name=_("Campaign"), blank=True, null=True, related_name='couponscampaign')
    cashback_value = models.IntegerField(_("Cashback Value"),default=0,
                                         help_text=_("Cashback Value for coupon with cashback. 0 means no cashback entry."))
    cashback_type = models.CharField(_("Cashback Type"), max_length=20, blank=True,null=True, choices=COUPON_TYPES,
                                     help_text=_("Mandatory if cashback value"))
    cashback_amt_limit = models.IntegerField(_("Cashback Limit"),
                                       help_text=_("For Percentage cashback, this is the amount limit for which coupon can be used"),
                                       blank=True,null=True)
    cashback_applicable_to = MultiSelectField(_("Cashback Applicable To"),max_length=20,
                                              choices=COUPON_APPLICATION_TYPES)
    how_it_works = models.CharField(_("How It Works"),max_length=255,null=True,blank=True)
    title = models.CharField(_("Title"),max_length=64)
    packages = models.ManyToManyField(Package,related_name="coupon_packages")

    objects = CouponManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    def expired(self, booking=None):
        if booking and booking.pickup_time:
            return self.valid_until is not None and self.valid_until < booking.pickup_time
        else:
            return self.valid_until is not None and self.valid_until < timezone.now()

    def is_valid(self,app_version):
        if app_version:
            return (self.is_cashback and app_version > 34) or not self.is_cashback
        else:
            return (not self.is_cashback)

    @classmethod
    def generate_code(cls, prefix=""):
        code = "".join(random.choice(Coupon.CODE_CHARS) for i in range(Coupon.CODE_LENGTH))
        return prefix + code


@python_2_unicode_compatible
class Campaign(CreatedAtAbstractBase):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)
    show_to_user = models.BooleanField(_("Show to User"),default=False)
    city = models.ManyToManyField(City, verbose_name=_("City"))

    class Meta:
        ordering = ['name']
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self):
        return self.name

    def get_cities(self):
        return ",".join([c.name for c in self.city.all()])
