# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0162_auto_20161122_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='followup',
            name='comm_mode',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'How was the customer communicated?', choices=[(1, b'Call'), (2, b'WhatsApp'), (3, b'SMS'), (4, b'Email')]),
        ),
    ]
