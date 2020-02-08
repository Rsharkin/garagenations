# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0274_auto_20170807_2245'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='workshopresources',
            unique_together=set([]),
        ),
    ]
