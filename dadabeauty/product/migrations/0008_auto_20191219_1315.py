# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-19 05:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_auto_20191218_2134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku_source',
            name='sku_id',
        ),
        migrations.RemoveField(
            model_name='sku_source',
            name='source_id',
        ),
        migrations.AddField(
            model_name='sku',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='折扣价'),
        ),
        migrations.AddField(
            model_name='sku',
            name='feature',
            field=models.CharField(default='', max_length=100, verbose_name='特点'),
        ),
        migrations.AddField(
            model_name='sku',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='价格'),
        ),
        migrations.AddField(
            model_name='sku',
            name='source_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='product.Source'),
        ),
        migrations.AddField(
            model_name='sku',
            name='source_url',
            field=models.URLField(default='', verbose_name='来源网址'),
        ),
        migrations.AlterField(
            model_name='sku',
            name='default_img_url',
            field=models.URLField(default='', verbose_name='sku图片'),
        ),
        migrations.DeleteModel(
            name='sku_source',
        ),
    ]