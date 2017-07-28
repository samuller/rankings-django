# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-28 08:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


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
                ('min_teams_per_match', models.IntegerField(default=2)),
                ('max_teams_per_match', models.IntegerField(blank=True, null=True)),
                ('min_players_per_team', models.IntegerField(default=1)),
                ('max_players_per_team', models.IntegerField(blank=True, default=1, null=True)),
                ('about', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'activity',
            },
        ),
        migrations.CreateModel(
            name='AdhocTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'adhoc_team',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.IntegerField(blank=True, null=True)),
                ('submittor', models.TextField(blank=True, null=True)),
                ('position', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.IntegerField(blank=True, null=True)),
                ('submittor', models.TextField(blank=True, null=True)),
                ('validated', models.IntegerField(blank=True, null=True)),
                ('activity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Activity')),
            ],
            options={
                'db_table': 'gamesession',
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
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Activity')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player')),
            ],
            options={
                'db_table': 'ranking',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.IntegerField(blank=True, null=True)),
                ('submittor', models.TextField(blank=True, null=True)),
                ('ranking', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Game')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='previous.AdhocTeam')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SkillHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.TextField(blank=True, null=True)),
                ('mu', models.FloatField(blank=True, null=True)),
                ('sigma', models.FloatField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Result')),
            ],
            options={
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
                'db_table': 'skill_type',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated', models.IntegerField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.AdhocTeam')),
            ],
            options={
                'db_table': 'team_member',
            },
        ),
        migrations.AddField(
            model_name='game',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='previous.GameSession'),
        ),
        migrations.AddField(
            model_name='adhocteam',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.GameSession'),
        ),
        migrations.AddField(
            model_name='activity',
            name='skill_type',
            field=models.ForeignKey(blank=True, db_column='skill_type', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.SkillType'),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('player', 'team')]),
        ),
        migrations.AlterUniqueTogether(
            name='skillhistory',
            unique_together=set([('player', 'result')]),
        ),
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('player', 'activity')]),
        ),
    ]
