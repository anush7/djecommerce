# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-25 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20160625_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='quantity_allocated',
            field=models.IntegerField(default=0),
        ),
    ]
