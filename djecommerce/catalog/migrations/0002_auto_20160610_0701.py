# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-10 07:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='productattribute',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_attributes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productattribute',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_attributes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='attributes',
            field=models.ManyToManyField(through='catalog.ProductAttributeValue', to='catalog.ProductAttribute'),
        ),
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(through='catalog.ProductCategory', to='catalog.CatalogCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='catalogcategory',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_categories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='catalogcategory',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_categories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='catalogcategory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalog.CatalogCategory'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='categories',
            field=models.ManyToManyField(to='catalog.CatalogCategory'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_catalogs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='catalog',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_catalogs', to=settings.AUTH_USER_MODEL),
        ),
    ]
