# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-19 11:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_auto_20191219_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku_img',
            name='sku_id',
        ),
        migrations.DeleteModel(
            name='Sku_img',
        ),
    ]
