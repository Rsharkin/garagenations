# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20160503_1751'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billitem',
            old_name='bill_amt',
            new_name='amount',
        ),
    ]
