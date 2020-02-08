# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0231_auto_20170323_1040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referralcode',
            name='campaign',
        ),
    ]
