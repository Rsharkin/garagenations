# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20160503_1402'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billitem',
            name='booking_package',
        ),
        migrations.AddField(
            model_name='billitem',
            name='package',
            field=models.ForeignKey(default=1, to='core.PackagePrice'),
            preserve_default=False,
        ),
    ]
