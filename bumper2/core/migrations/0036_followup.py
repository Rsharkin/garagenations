# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20160503_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='Followup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('booking', models.ForeignKey(to='core.Booking')),
                ('updated_by', models.ForeignKey(help_text=b'Person how punched in this entry', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
