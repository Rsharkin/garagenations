# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0123_auto_20160824_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinquiry',
            name='assigned_to',
            field=models.ForeignKey(related_name='userinquiry_assigned_to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
