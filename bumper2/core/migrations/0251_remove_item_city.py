# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0250_auto_20170512_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='city',
        ),
    ]
