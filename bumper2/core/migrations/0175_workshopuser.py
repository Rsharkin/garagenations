# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0174_auto_20161223_1635'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkshopUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('role', models.PositiveSmallIntegerField(choices=[(1, b'Bumper Workshop Executive'), (2, b'Bumper Workshop Asst Manager'), (3, b'Bumper Workshop Manager'), (4, b'Workshop Owner')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('workshop', models.ForeignKey(to='core.Workshop')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
