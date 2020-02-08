# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_package_popular'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='internal',
            field=models.BooleanField(default=True, help_text=b'These packages price can be editable from backend.'),
        ),
    ]
