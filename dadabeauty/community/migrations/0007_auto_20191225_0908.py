# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-25 01:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0006_likecommunity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='likecommunity',
            old_name='isActive',
            new_name='is_active',
        ),
    ]
