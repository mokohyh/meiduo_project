# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-09-23 12:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='area',
            old_name='parente',
            new_name='parent',
        ),
    ]
