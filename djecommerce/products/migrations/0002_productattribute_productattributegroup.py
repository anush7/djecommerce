# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-11 13:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0005_auto_20160611_1330'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('type', models.CharField(choices=[('text', 'Text'), ('integer', 'Integer'), ('boolean', 'True / False'), ('float', 'Float'), ('date', 'Date'), ('file', 'File'), ('image', 'Image')], default='text', max_length=20)),
                ('status', models.CharField(default='A', max_length=1)),
                ('is_trashed', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cat_attributes', to='catalog.CatalogCategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_attributes', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_attributes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('order_by', models.IntegerField(default=1)),
                ('status', models.CharField(default='A', max_length=1)),
            ],
        ),
    ]
