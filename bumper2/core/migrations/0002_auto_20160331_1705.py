# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bumperuser',
            name='email',
            field=models.EmailField(help_text=b"This will be user's email.", max_length=254, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='phone',
            field=models.CharField(max_length=10, unique=True, null=True, blank=True),
        ),
    ]
