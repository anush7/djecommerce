# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-07 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecuser',
            name='braintree_id',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
