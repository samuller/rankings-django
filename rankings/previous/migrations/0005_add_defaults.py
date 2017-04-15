# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-11 16:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('previous', '0004_ranking_to_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.AdhocTeam'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity',
            name='skill_type',
            field=models.ForeignKey(blank=True, db_column='skill_type', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.SkillType'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='max_players_per_team',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='min_players_per_team',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='activity',
            name='min_teams_per_match',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='activity',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Activity'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ranking',
            name='player',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='result',
            name='team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='previous.AdhocTeam'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='skillhistory',
            name='player',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='skillhistory',
            name='result',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Result'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='teammember',
            name='player',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='previous.Player'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('player', 'activity')]),
        ),
        migrations.AlterUniqueTogether(
            name='skillhistory',
            unique_together=set([('player', 'result')]),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('player', 'team')]),
        ),
    ]