# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_package_website_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='website_url',
            new_name='website_desc_url',
        ),
    ]
