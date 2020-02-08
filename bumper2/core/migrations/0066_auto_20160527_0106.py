# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_package_popular'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notifications',
            name='mandrill_template',
        ),
        migrations.RemoveField(
            model_name='notifications',
            name='use_mandrill',
        ),
        migrations.AddField(
            model_name='notifications',
            name='template_folder_name',
            field=models.CharField(help_text=b'If use_template is true then name of the folder of mailer template is required.', max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='notifications',
            name='use_template',
            field=models.BooleanField(default=False, help_text=b'Using file template as content?'),
        ),
    ]
