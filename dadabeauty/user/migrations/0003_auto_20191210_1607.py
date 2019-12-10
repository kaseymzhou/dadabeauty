# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-10 08:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20191210_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='fans_id',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, related_name='fans_id', to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='followed_id',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, related_name='followed_id', to='user.UserProfile'),
        ),
    ]
