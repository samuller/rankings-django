# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
import datetime

from .utils import cardinalToOrdinal


MANAGED = False

class Activity(models.Model):
    """
    A type of activity for which new match results can be recorded.
    """
    id = models.TextField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    skill_type = models.ForeignKey('SkillType', models.DO_NOTHING, db_column='skill_type', blank=True, null=True)
    min_teams_per_match = models.IntegerField(default=2)
    max_teams_per_match = models.IntegerField(blank=True, null=True)
    min_players_per_team = models.IntegerField(default=1)
    max_players_per_team = models.IntegerField(blank=True, null=True, default=1)
    about = models.TextField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'activity'

    def to_dict_with_url(self):
        result = self.__dict__
        result["url"] = result["id"]
        return result

    def __str__(self):
        return self.name


class SubmittedData(models.Model):
    datetime = models.IntegerField(blank=True, null=True)
    submittor = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class GameSession(SubmittedData):
    # id = models.IntegerField(primary_key=True)  # AutoField?
    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'gamesession'

    def summary_str_2(self):
        """
        A string summarising the game result.
        """
        summary = self.to_dict_with_teams()
        
        verb = "played"
        if summary['team1_rank'] < summary['team2_rank']:
          verb = "won"
        if summary['team1_rank'] > summary['team2_rank']:
          verb = "lost"
        if summary['team1_rank'] == summary['team2_rank']:
          verb = "tied"
        
        return ("[%s] ID: %s, %s %s vs. %s" % 
            (summary['activity_id'], summary['id'], summary['team1'], verb, summary['team2']))

    def summary_str(self):
        result_str = ", ".join(["%s: %s" % (cardinalToOrdinal(team.ranking), team.members_str())
          for team in AdhocTeam.objects.filter(result=self)])
        return ("[%s] %s result: %s" % (self.id, self.activity.id, result_str))

    def to_dict_with_teams(self):
        result = self.__dict__
        result["relative_date"] = datetime.datetime.fromtimestamp(self.datetime)
        result["date"] = datetime.datetime.fromtimestamp(self.datetime)
        teams = AdhocTeam.objects.filter(result=self)
        cnt = 0
        for team in teams:
            result["team%s" % (cnt+1)] = team.members_str()
            result["team%s_rank" % (cnt + 1)] = team.ranking
            cnt += 1

        return result

    def get_ranked_teams(self):
        return [team for team in AdhocTeam.objects.filter(result=self).order_by('ranking')]

    def __str__(self):
        return "GameSession of %s @ %s (Submitter: %s)" % (self.activity, self.datetime, self.submittor)


class Game(SubmittedData):
    session = models.ForeignKey(GameSession, models.DO_NOTHING)


class Result(SubmittedData):
    game = models.ForeignKey(Game, models.DO_NOTHING)


class AdhocTeam(models.Model):
    # id = models.IntegerField(primary_key=True)  # AutoField?
    result = models.ForeignKey(GameSession, models.DO_NOTHING, blank=True, null=True)
    ranking = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'adhoc_team'

    def members_str(self):
        members = [str(m.player) for m in TeamMember.objects.filter(team=self)]
        if len(members) == 0:
          return ""
        if len(members) == 1:
          return members[0]
        return ", ".join(members[:-1]) + " & " + members[-1]

    def __str__(self):
        return "Team ranked %s @ %s" % (self.ranking, self.result)


class Player(models.Model):
    # id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.TextField()
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'player'

    def to_dict_with_skill(self, activity_id):
        ranks = Ranking.objects.filter(player=self,activity_id=activity_id)
        result = self.__dict__
        result["skill"] = 0
        result["mu"] = 0
        result["sigma"] = 0
        if len(ranks) > 0:
            result["skill"] = ranks[0].calc_skill()
            result["mu"] = ranks[0].mu
            result["sigma"] = ranks[0].sigma
        return result

    def __str__(self):
        return self.name


class Ranking(models.Model):
    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'ranking'
        unique_together = (('player', 'activity'),)

    def calc_skill(self):
        min_range = 0  # skill_type.min_skill_range
        max_range = 50  # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill

    def __str__(self):
        return "%s @ %s: (%s, %s)" % (self.player, self.activity, self.mu, self.sigma)


class ResultSet(models.Model):
    # id = models.IntegerField(primary_key=True)  # AutoField?

    class Meta:
        managed = MANAGED
        db_table = 'result_set'


class ResultSetMember(models.Model):
    result_set = models.ForeignKey(ResultSet, models.DO_NOTHING)
    result = models.ForeignKey(Player, models.DO_NOTHING)

    class Meta:
        managed = MANAGED
        db_table = 'result_set_member'
        unique_together = (('result_set', 'result'),)


class SkillHistory(models.Model):
    result = models.ForeignKey(Result, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    activity_id = models.TextField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'skill_history'
        unique_together = (('player', 'result'),)

    def calc_skill(self):
        min_range = 0 # skill_type.min_skill_range
        max_range = 50 # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill

    def __str__(self):
        return "[%s] %s @ %s: (%s, %s)" % (self.result, self.player, self.activity_id, self.mu, self.sigma)


class SkillType(models.Model):
    id = models.TextField(primary_key=True)
    min_skill_range = models.FloatField(default=0)
    max_skill_range = models.FloatField(default=50)
    initial_mean = models.FloatField(default=25)
    initial_std_dev = models.FloatField(default=25/3.0)
    dynamics_factor = models.FloatField(default=25/300.0)
    skill_chain = models.FloatField(default=25/6.0)
    draw_chance = models.FloatField(default=0.1)

    class Meta:
        managed = MANAGED
        db_table = 'skill_type'

    def __str__(self):
        return "Range: %s-%s, Initial: %s,%s, Skill chain: %s, Draw: %s, Dynamics: %s" % (
            self.min_skill_range, self.max_skill_range,
            self.initial_mean, self.initial_std_dev,
            self.skill_chain, self.draw_chance, self.dynamics_factor)


class TeamMember(models.Model):
    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = 'team_member'
        unique_together = (('player', 'team'),)

    def __str__(self):
        return "%s was member of %s" % (self.player, self.team)
