# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-12-01 18:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PandDDL', '0017_auto_20181130_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doublesmatch',
            name='away1finish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='away1finish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='away1finish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='away2finish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='away2finish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='away2finish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='awaymaximums1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='awaymaximums2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home1finish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home1finish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home1finish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home2finish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home2finish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='home2finish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='homemaximums1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='doublesmatch',
            name='homemaximums2',
            field=models.IntegerField(blank=True, default=0, null=True),
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
            model_name='singlesmatch',
            name='awayfinish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='awayfinish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='awayfinish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='awaymaximums',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='homefinish1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='homefinish2',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='homefinish3',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='singlesmatch',
            name='homemaximums',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
