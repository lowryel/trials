# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2021-08-11 12:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20210810_2103'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='login',
            new_name='signup',
        ),
    ]
