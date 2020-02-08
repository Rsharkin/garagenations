# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0254_auto_20170524_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingchecklist',
            name='mismatch',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='followup',
            name='comm_mode',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'How was the customer communicated?', choices=[(1, b'Call'), (2, b'WhatsApp'), (3, b'SMS'), (4, b'Email'), (5, b'Executive App'), (6, b'Push'), (7, b'Web Chat'), (8, b'Helpshift')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='label',
            field=models.PositiveSmallIntegerField(help_text=b'This is to identify which screen will open in UI', null=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral'), (6, b'RateUs'), (7, b'FillProfile'), (8, b'FillCarInfo'), (9, b'EOD'), (10, b'Req. Loc.'), (11, b'CancelRetarget')]),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='push_level',
            field=models.SmallIntegerField(default=1, null=True, blank=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral'), (6, b'RateUs'), (7, b'FillProfile'), (8, b'FillCarInfo'), (9, b'EOD'), (10, b'Req. Loc.'), (11, b'CancelRetarget')]),
        ),
    ]
