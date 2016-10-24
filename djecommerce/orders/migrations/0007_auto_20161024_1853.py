# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-24 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20161024_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetails',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='processed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='returned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
    ]
