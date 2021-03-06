# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-26 18:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20161025_0841'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('percentage', models.DecimalField(decimal_places=5, max_digits=10)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
    ]
