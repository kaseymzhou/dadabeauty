# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-18 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20191218_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image_url',
            field=models.ImageField(default='', upload_to='myfile', verbose_name='头像'),
        ),
    ]
