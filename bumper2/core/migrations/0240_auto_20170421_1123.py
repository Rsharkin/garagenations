# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import models, migrations
from core.models.referral import ReferralCode
from django.contrib.auth import get_user_model


def create_referralcodes(apps, schema_editor):
    User = get_user_model()
    users = User.objects.filter(is_active=True, phone__isnull=False)
    for user in users:
        ReferralCode.objects.create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0239_auto_20170419_1257'),
    ]

    operations = [
        migrations.RunPython(create_referralcodes, reverse_code=migrations.RunPython.noop),
    ]
