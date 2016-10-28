# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-28 02:49
from __future__ import unicode_literals

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_auto_20161027_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to=products.models.get_product_image_path),
        ),
    ]
