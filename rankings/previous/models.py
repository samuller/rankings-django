# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Activity(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    skill_type = models.ForeignKey('SkillType', models.DO_NOTHING, db_column='skill_type', blank=True, null=True)
    min_teams_per_match = models.IntegerField()
    max_teams_per_match = models.IntegerField(blank=True, null=True)
    min_players_per_team = models.IntegerField()
    max_players_per_team = models.IntegerField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity'


class AdhocTeam(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    result = models.ForeignKey('Result', models.DO_NOTHING, blank=True, null=True)
    ranking = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adhoc_team'


class Player(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.TextField()
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player'


class Ranking(models.Model):
    activity = models.ForeignKey(Activity, models.DO_NOTHING, primary_key=True)
    player = models.ForeignKey(Player, models.DO_NOTHING, primary_key=True)
    active = models.IntegerField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ranking'
        unique_together = (('player', 'activity'),)


class Result(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    activity = models.ForeignKey(Activity, models.DO_NOTHING, blank=True, null=True)
    datetime = models.IntegerField(blank=True, null=True)
    validated = models.IntegerField(blank=True, null=True)
    submittor = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result'


class ResultSet(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?

    class Meta:
        managed = False
        db_table = 'result_set'


class ResultSetMember(models.Model):
    result_set = models.ForeignKey(ResultSet, models.DO_NOTHING, primary_key=True)
    result = models.ForeignKey(Player, models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = 'result_set_member'
        unique_together = (('result_set', 'result'),)


class SkillHistory(models.Model):
    result = models.ForeignKey(Result, models.DO_NOTHING, primary_key=True)
    player = models.ForeignKey(Player, models.DO_NOTHING, primary_key=True)
    activity_id = models.TextField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'skill_history'
        unique_together = (('player', 'result'),)


class SkillType(models.Model):
    id = models.TextField(primary_key=True)
    min_skill_range = models.FloatField()
    max_skill_range = models.FloatField()
    initial_mean = models.FloatField()
    initial_std_dev = models.FloatField()
    dynamics_factor = models.FloatField()
    skill_chain = models.FloatField()
    draw_chance = models.FloatField()

    class Meta:
        managed = False
        db_table = 'skill_type'


class TeamMember(models.Model):
    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING, primary_key=True)
    player = models.ForeignKey(Player, models.DO_NOTHING, primary_key=True)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_member'
        unique_together = (('player', 'team'),)
