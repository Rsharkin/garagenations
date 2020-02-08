# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0242_auto_20170421_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='campaign',
        ),
    ]
