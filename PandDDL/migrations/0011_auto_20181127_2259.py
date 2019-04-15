# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-27 22:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('PandDDL', '0010_auto_20181127_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='admin',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fixture',
            name='awayteam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away', to='PandDDL.Team'),
        ),
        migrations.AlterField(
            model_name='fixture',
            name='hometeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home', to='PandDDL.Team'),
        ),
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PandDDL.Team'),
        ),
        migrations.AlterField(
            model_name='pointsdeduction',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PandDDL.Team'),
        ),
    ]
