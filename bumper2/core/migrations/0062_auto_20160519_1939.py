# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_package_long_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercredit',
            name='user',
            field=models.ForeignKey(related_name='user_credit', to=settings.AUTH_USER_MODEL),
        ),
    ]
