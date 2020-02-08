# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_media'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(default=b'app', max_length=5, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber')])),
                ('user', models.ForeignKey(related_name='booking', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message_type', models.SmallIntegerField(help_text=b'Type of message.', choices=[(1, b'SMS'), (3, b'EMAIL'), (2, b'PUSH')])),
                ('subject', models.CharField(max_length=256, null=True)),
                ('message', models.TextField(help_text=b'This will be empty for email where content of email is not stored.', null=True, blank=True)),
                ('message_send_level', models.SmallIntegerField(default=1, choices=[(1, b'All'), (2, b'Specific')])),
                ('direction', models.SmallIntegerField(choices=[(1, b'BumperToCustomer'), (2, b'BumperToDealer'), (3, b'CustomerToDealer'), (4, b'DealerToCustomer'), (5, b'BumperToOps')])),
                ('viewed_by', models.IntegerField(default=0, help_text=b'Will be updated once user views the message.(For push notifications only)')),
                ('label', models.PositiveSmallIntegerField(help_text=b'This is to identify which screen will open in UI', null=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral')])),
                ('booking', models.ForeignKey(blank=True, to='core.Booking', null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='MessageUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_to', models.CharField(help_text=b'Phone number for SMS, email address for email. Null in case of push notifications', max_length=1024, null=True)),
                ('gateway_api_response', models.CharField(max_length=64, null=True)),
                ('delivery_report', models.CharField(max_length=64, null=True, blank=True)),
                ('delivered_dt', models.DateTimeField(help_text=b'Timestamp of delivery or receipt of delivery.', null=True)),
                ('retry_count', models.IntegerField(default=0, help_text=b'Number of tries to send in case of failure.', null=True)),
                ('viewed_dt', models.DateTimeField(help_text=b'This is when mobile user reads the msg.', null=True)),
                ('message', models.ForeignKey(to='core.Messages')),
                ('user', models.ForeignKey(related_name='message_user', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'Will be empty when sending mail/sms directly to email or sms like for OPS mails', null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
