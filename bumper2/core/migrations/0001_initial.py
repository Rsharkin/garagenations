# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='BumperUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.UUIDField(help_text=b'This is username of user.', unique=True)),
                ('email', models.EmailField(help_text=b"This will be user's email.", max_length=254, null=True, blank=True)),
                ('name', models.CharField(help_text=b'this is name of alt. customer.', max_length=255, null=True, blank=True)),
                ('phone', models.CharField(max_length=10, null=True, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_otp_validated', models.BooleanField(default=False)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('utm_source', models.CharField(max_length=128, null=True, blank=True)),
                ('utm_medium', models.CharField(max_length=128, null=True, blank=True)),
                ('utm_campaign', models.CharField(max_length=128, null=True, blank=True)),
                ('designation', models.CharField(max_length=64, null=True, blank=True)),
                ('company_name', models.CharField(max_length=128, null=True, blank=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('is_denting_active', models.BooleanField(default=True)),
                ('is_wash_active', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(to='core.State'),
        ),
        migrations.AddField(
            model_name='bumperuser',
            name='city',
            field=models.ForeignKey(blank=True, to='core.City', null=True),
        ),
        migrations.AddField(
            model_name='bumperuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='bumperuser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
    ]
