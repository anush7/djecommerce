# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-02 05:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_useraddress_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_placed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]