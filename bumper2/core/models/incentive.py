from django.db import models
from core.models import common, coupons
from core.models import master


class IncentiveEvent(common.CreatedAtAbstractBase):
    TP_PAYTM = 1

    TP_CHOICES = (
        (TP_PAYTM, "PayTM"),
    )

    #is_promised = models.BooleanField(default=True)
    name = models.CharField(max_length=64, help_text="This is used in code. Do not change it.")
    #promised_name = models.CharField(max_length=64, help_text="This is used in code. Do not change it.")
    active = models.BooleanField(default=True)
    coupon = models.ForeignKey(coupons.Coupon, null=True, blank=True)
    tp_cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                  help_text="Third Party Cash Amount")
    tp = models.PositiveSmallIntegerField(choices=TP_CHOICES, null=True, blank=True,
                                          help_text="Third Party Name")
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True,
                                   help_text="Keep it empty if you want this to run unlimited.")
    notifications = models.ManyToManyField(master.Notifications, blank=True)
    #promised_event = models.ForeignKey('self', blank=True, null=True, related_name="promised_incentive")

    def __unicode__(self):
        return "{}".format(self.name)
