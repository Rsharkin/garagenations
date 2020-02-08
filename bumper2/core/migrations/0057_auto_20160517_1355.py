# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_auto_20160516_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='bumperuser',
            name='merged_to',
            field=models.ForeignKey(related_name='user_merged_to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='bumperuser',
            name='ops_phone',
            field=models.CharField(max_length=10, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='email',
            field=models.EmailField(help_text=b"This will be user's email.", max_length=254, null=True, blank=True),
        ),
    ]
