# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-03 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_tax_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
