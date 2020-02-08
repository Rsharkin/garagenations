# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0112_auto_20160808_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanelprice',
            name='internal',
            field=models.BooleanField(default=False, help_text=b'This panel price can only be seen on backend.'),
        ),
    ]
