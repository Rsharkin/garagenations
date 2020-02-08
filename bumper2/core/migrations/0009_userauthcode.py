# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160411_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAuthCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('phone', models.CharField(max_length=10, null=True)),
                ('auth_code', models.CharField(max_length=6)),
                ('expiry_dt', models.DateTimeField()),
                ('system_alert_sent', models.BooleanField(default=False, help_text=b'Marks whether alert has been sent for failed OTP, to avoid duplicates alerts.')),
                ('user', models.ForeignKey(related_name='user_auth_code', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
