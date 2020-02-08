# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0209_auto_20170214_1545'),
    ]

    operations = [
        migrations.RenameModel('CarModelVersion', 'CarModelVariant')
    ]
