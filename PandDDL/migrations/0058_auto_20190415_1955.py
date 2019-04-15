# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-04-15 18:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PandDDL', '0057_auto_20190415_1931'),
    ]

    operations = [
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
            name='dateadded',
            field=models.DateField(default=datetime.datetime(2019, 4, 15, 19, 55, 2, 969000)),
            preserve_default=False,
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
