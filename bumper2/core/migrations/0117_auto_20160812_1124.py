# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0116_auto_20160812_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='followup',
            field=models.ManyToManyField(related_name='booking_followup', to='core.Followup'),
        ),
        migrations.AlterField(
            model_name='followup',
            name='booking',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='followup',
            name='updated_by',
            field=models.ForeignKey(help_text=b'Person who punched this entry', to=settings.AUTH_USER_MODEL),
        ),
    ]
