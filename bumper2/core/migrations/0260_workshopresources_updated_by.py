# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0259_auto_20170711_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshopresources',
            name='updated_by',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, help_text=b'Person who punched this entry'),
            preserve_default=False,
        ),
    ]
