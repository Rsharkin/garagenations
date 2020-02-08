# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_package_internal'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanel',
            name='internal',
            field=models.BooleanField(default=True, help_text=b'These panels price can be editable from backend.'),
        ),
    ]
