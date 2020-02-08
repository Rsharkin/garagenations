# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0275_auto_20170807_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workshopresources',
            name='workshop',
            field=models.ForeignKey(related_name='workshopresource', to='core.Workshop'),
        ),
    ]
