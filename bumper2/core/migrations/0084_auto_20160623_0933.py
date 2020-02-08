# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_bookingdiscount_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageuser',
            name='message',
            field=models.ForeignKey(related_name='user_message', to='core.Messages'),
        ),
    ]
