import random
import string

from django.db import IntegrityError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from simple_history.models import HistoricalRecords

from core.models.common import CreatedAtAbstractBase
from core.models.master import Notifications
from core.models.users import BumperUser


@python_2_unicode_compatible
class ReferralCampaign(CreatedAtAbstractBase):
    # CREATE_USER = 'CREATE_USER'
    # CAR_PICKED_UP = 'CAR_PICKED_UP'

    name = models.CharField(_("Name"), max_length=255, unique=True,
                            help_text=_("Do not change this after creation. It is used in code"))
    description = models.TextField(_("Description"), blank=False, null=False)
    referrer_credit = models.IntegerField(_("Referrer Credit"), null=True, blank=True,
                                          help_text=_("This will be given to user who is referring."))
    referred_credit = models.IntegerField(_("Referred Credit"), null=True, blank=True,
                                          help_text=_("This will be given to user who got referred."))
    referrer_tp_cash = models.IntegerField(_("Referrer Paytm Cash"), null=True, blank=True,
                                          help_text=_("This will be given to user who is referring."))
    referred_tp_cash = models.IntegerField(_("Referred Paytm Cash"), null=True, blank=True,
                                           help_text=_("This will be given to user who got referred."))
    notifications = models.ManyToManyField(Notifications, blank=True)
    active = models.BooleanField(default=False)
    terms = models.TextField(_("Terms And Conditions"), null=False, blank=False,
                             help_text=_("This will be shown to user"))
    share_message = models.TextField(_("Share Message"), null=False, blank=False,
                                     help_text=_("This message will be sent while sharing. "
                                                 "Use {%referral_code%} to include referral code"))
    share_title = models.TextField(_("Share Title"), null=False, blank=False,
                                   help_text=_("This title will be sent while sharing."
                                               " Use {%referral_code%} to include referral code"))

    history = HistoricalRecords()

    class Meta:
        ordering = ['name']
        verbose_name = _("Referral Campaign")
        verbose_name_plural = _("Referral Campaigns")

    def __str__(self):
        return self.name


class ReferralCodeManager(models.Manager):
    def create_code(self, user=None, prefix=""):
        referral_code = self.create(
            code=ReferralCode.generate_code(prefix),
            user=user,
        )
        try:
            referral_code.save()
        except IntegrityError:
            # Try again with other code
            return ReferralCode.objects.create_code(user, prefix)
        else:
            return referral_code


@python_2_unicode_compatible
class ReferralCode(CreatedAtAbstractBase):
    CODE_LENGTH = 8
    CODE_CHARS = string.ascii_uppercase + string.digits

    code = models.CharField(_("Code"), max_length=30, unique=True,
                            help_text=_("Leaving this field empty will generate a random code."))
    user = models.ForeignKey(BumperUser, verbose_name=_("User"))
    active = models.BooleanField(default=True)

    objects = ReferralCodeManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = _("ReferralCode")
        verbose_name_plural = _("Referral Codes")

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ReferralCode.generate_code()
        super(ReferralCode, self).save(*args, **kwargs)

    @classmethod
    def generate_code(cls, prefix=""):
        code = "".join(random.choice(ReferralCode.CODE_CHARS) for i in range(ReferralCode.CODE_LENGTH))
        return prefix + code


@python_2_unicode_compatible
class Referral(CreatedAtAbstractBase):
    referrer = models.ForeignKey(BumperUser, related_name="referreruser", help_text="Existing user referred new user")
    referred = models.ForeignKey(BumperUser, related_name="referreduser", help_text="New user referred by existing")
    # campaign = models.ForeignKey(ReferralCampaign)

    class Meta:
        verbose_name = _("Referral")
        verbose_name_plural = _("Referrals")

    def __str__(self):
        return "%s-%s" % (self.referrer,self.referred)
