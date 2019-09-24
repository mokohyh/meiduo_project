# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-09-23 11:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='名称')),
                ('parente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subs', to='area.Area', verbose_name='上级行政区划')),
            ],
            options={
                'verbose_name_plural': '省市区',
                'verbose_name': '省市区',
                'db_table': 'tb_areas',
            },
        ),
    ]
