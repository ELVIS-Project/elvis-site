# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-23 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='parent_cart_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
