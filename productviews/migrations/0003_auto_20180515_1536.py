# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-05-15 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productviews', '0002_auto_20180515_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='view',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date viewed'),
        ),
    ]
