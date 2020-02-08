# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0272_usercar_new_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshopresources',
            name='polishers',
            field=models.IntegerField(default=1),
        ),
    ]
