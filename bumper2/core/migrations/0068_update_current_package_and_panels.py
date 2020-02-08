# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import models, migrations
from core.models.master import Package, CarPanel

def update_packages(apps, schema_editor):
    # set internal to False for current packages
    Package.objects.all().update(internal=False)


def update_panels(apps, schema_editor):
    # set internal to False for current packages
    CarPanel.objects.all().update(internal=False)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_carpanel_internal'),
    ]

    operations = [
        migrations.RunPython(update_packages, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_panels, reverse_code=migrations.RunPython.noop),
    ]
