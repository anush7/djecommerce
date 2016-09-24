# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-24 09:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_egroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='egroup',
            name='is_export',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='egroup',
            name='is_import',
            field=models.BooleanField(default=False),
        ),
    ]
