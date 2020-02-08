# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_auto_20160512_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hooks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action_taken', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Hooks',
            },
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(help_text=b'Do not change this, this is used in code. Eg. TempName1', max_length=32)),
                ('type', models.SmallIntegerField(choices=[(1, b'Email'), (2, b'SMS'), (3, b'Push')])),
                ('priority', models.SmallIntegerField(default=1, help_text=b'Do not change this, this is for the scheduler.')),
                ('to', models.CharField(help_text=b'Emails comma separated, For SMS this will be phone number without +91.', max_length=64)),
                ('cc', models.CharField(help_text=b'Comma separated values expected.', max_length=512, null=True, blank=True)),
                ('bcc', models.CharField(help_text=b'Comma separated values expected.', max_length=512, null=True, blank=True)),
                ('subject', models.CharField(max_length=128, null=True, blank=True)),
                ('template', models.TextField()),
                ('use_mandrill', models.BooleanField(default=False)),
                ('mandrill_template', models.CharField(max_length=64, null=True, blank=True)),
                ('only_for_user', models.BooleanField(default=False, help_text=b'In this case to field will not be used.')),
            ],
            options={
                'verbose_name_plural': 'Notifications',
            },
        ),
        migrations.AlterUniqueTogether(
            name='notifications',
            unique_together=set([('name', 'type')]),
        ),
        migrations.AddField(
            model_name='hooks',
            name='notification',
            field=models.ForeignKey(related_name='hook_notifications', to='core.Notifications'),
        ),
    ]
