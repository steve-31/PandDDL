# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-12-04 22:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PandDDL', '0023_auto_20181204_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='cupround',
            name='roundnumber',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cupfixture',
            name='awayteam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cupaway', to='PandDDL.Team'),
        ),
        migrations.AlterField(
            model_name='cupfixture',
            name='hometeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuphome', to='PandDDL.Team'),
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
