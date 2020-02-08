# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_auto_20160529_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanelprice',
            name='editable',
            field=models.BooleanField(default=False, help_text=b'If this is checked, that means price is editable'),
        ),
    ]
