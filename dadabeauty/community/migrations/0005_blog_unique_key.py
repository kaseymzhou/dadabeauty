# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-23 05:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_auto_20191223_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='unique_key',
            field=models.CharField(default='', max_length=32, verbose_name='标识'),
        ),
    ]
