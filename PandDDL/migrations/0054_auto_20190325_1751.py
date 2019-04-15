# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-03-25 17:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PandDDL', '0053_auto_20190321_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='agmminutes',
            name='location',
            field=models.CharField(default='Post Office', max_length=200),
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
        migrations.AlterField(
            model_name='result',
            name='opposition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opposition', to='PandDDL.Team'),
        ),
        migrations.AlterField(
            model_name='result',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team', to='PandDDL.Team'),
        ),
    ]
