# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0248_auto_20170504_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credittransaction',
            name='user',
            field=models.ForeignKey(related_name='user_credittrx', to=settings.AUTH_USER_MODEL),
        ),
    ]
