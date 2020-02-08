# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_carpanelprice_editable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carpanelprice',
            name='editable',
            field=models.BooleanField(default=False, help_text=b'This panel price can be editable from backend.'),
        ),
    ]
