# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-17 19:47
from __future__ import unicode_literals

from django.db import migrations, models

from ..models import MANAGED


def insert_default_skill_type(apps, schema_editor):
  SkillType = apps.get_model("previous", "SkillType")
  db_alias = schema_editor.connection.alias
  SkillType.objects.using(db_alias).create(
      id='default', min_skill_range=0, max_skill_range=50,
      initial_mean=25, initial_std_dev=25/3.0,
      dynamics_factor=25/300.0, skill_chain=25/6.0,
      draw_chance=0.1
  )


def delete_default_skill_type(apps, schema_editor):
    SkillType = apps.get_model("previous", "SkillType")
    db_alias = schema_editor.connection.alias
    SkillType.objects.using(db_alias).get(id="default").delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('min_teams_per_match', models.IntegerField()),
                ('max_teams_per_match', models.IntegerField(blank=True, null=True)),
                ('min_players_per_team', models.IntegerField()),
                ('max_players_per_team', models.IntegerField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'activity',
            },
        ),
        migrations.CreateModel(
            name='AdhocTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ranking', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'adhoc_team',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('email', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'player',
            },
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.IntegerField(blank=True, null=True)),
                ('mu', models.FloatField(blank=True, null=True)),
                ('sigma', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'ranking',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.IntegerField(blank=True, null=True)),
                ('validated', models.IntegerField(blank=True, null=True)),
                ('submittor', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'result',
            },
        ),
        migrations.CreateModel(
            name='ResultSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'result_set',
            },
        ),
        migrations.CreateModel(
            name='ResultSetMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'result_set_member',
            },
        ),
        migrations.CreateModel(
            name='SkillHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.TextField(blank=True, null=True)),
                ('mu', models.FloatField(blank=True, null=True)),
                ('sigma', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'skill_history',
            },
        ),
        migrations.CreateModel(
            name='SkillType',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('min_skill_range', models.FloatField(default=0)),
                ('max_skill_range', models.FloatField(default=50)),
                ('initial_mean', models.FloatField(default=25)),
                ('initial_std_dev', models.FloatField(default=8.333333333333334)),
                ('dynamics_factor', models.FloatField(default=0.08333333333333333)),
                ('skill_chain', models.FloatField(default=4.166666666666667)),
                ('draw_chance', models.FloatField(default=0.1)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'skill_type',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': MANAGED,
                'db_table': 'team_member',
            },
        ),
        migrations.RunPython(insert_default_skill_type, delete_default_skill_type),
    ]
