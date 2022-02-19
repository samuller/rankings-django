# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
import datetime

from .utils import cardinalToOrdinal


"""
A type of game.
"""


class Activity(models.Model):
    """
    A type of activity for which new match results can be recorded.
    """

    id = models.TextField(primary_key=True)
    url = models.TextField(unique=True, blank=False, null=False)
    name = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    skill_type = models.ForeignKey(
        "SkillType", models.DO_NOTHING, db_column="skill_type", blank=True, null=True
    )
    min_teams_per_match = models.IntegerField(default=2)
    max_teams_per_match = models.IntegerField(blank=True, null=True)
    min_players_per_team = models.IntegerField(default=1)
    max_players_per_team = models.IntegerField(blank=True, null=True, default=1)
    about = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "activity"

    def to_dict_with_url(self):
        result = self.__dict__
        # result["url"] = result["id"]
        return result

    def __str__(self):
        return self.name


"""
An abstract class for objects for recording how data was submitted.
"""


class SubmittedData(models.Model):
    datetime = models.IntegerField(blank=True, null=True)
    submittor = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


"""
A session of games played with the same players, at the same location, within a certain
period of time (see Game).
"""


class GameSession(SubmittedData):
    # id = models.IntegerField(primary_key=True)  # AutoField?
    activity = models.ForeignKey(Activity, models.DO_NOTHING, null=True)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "gamesession"

    def get_ranked_teams(self):
        return [
            team for team in AdhocTeam.objects.filter(result=self).order_by("ranking")
        ]

    def summary_str(self):
        result_str = ", ".join(
            [
                f"{cardinalToOrdinal(Result.objects.get(team=team).ranking)}: {team.members_str()}"
                for team in AdhocTeam.objects.filter(session=self)
            ]
        )
        return f"[{self.id}] {self.activity.id} result: {result_str}"

    def __str__(self):
        return f"Game of {self.activity} @ {self.datetime} (Submitter: {self.submittor})"


"""
A group of players that formed a team for a session (see TeamMember).
"""


class AdhocTeam(models.Model):
    session = models.ForeignKey(GameSession, models.DO_NOTHING, null=True)

    class Meta:
        db_table = "adhoc_team"

    def members_str(self):
        members = [str(m.player) for m in TeamMember.objects.filter(team=self)]
        if len(members) == 0:
            return ""
        if len(members) == 1:
            return members[0]
        return ", ".join(members[:-1]) + " & " + members[-1]

    def __str__(self):
        return f"Team {self.id}"


"""
A single game played within a session.
"""


class Game(SubmittedData):
    session = models.ForeignKey(GameSession, models.DO_NOTHING)
    position = models.IntegerField(default=0)

    def summary_str_2(self):
        """
        A string summarising the game result.
        """
        summary = self.to_dict_with_teams()

        verb = "played"
        if summary["team1_rank"] < summary["team2_rank"]:
            verb = "won"
        if summary["team1_rank"] > summary["team2_rank"]:
            verb = "lost"
        if summary["team1_rank"] == summary["team2_rank"]:
            verb = "tied"

        return f"[{summary['activity_id']}] ID: {summary['id']}, {summary['team1']} {verb} vs. {summary['team2']}"

    def to_dict_with_teams(self):
        result = self.__dict__
        result["relative_date"] = datetime.datetime.fromtimestamp(self.datetime)
        result["date"] = datetime.datetime.fromtimestamp(self.datetime)
        teams = AdhocTeam.objects.filter(session=self.session)
        cnt = 0
        for team in teams:
            result[f"team{cnt + 1}"] = team.members_str()
            team_result = Result.objects.get(game=self, team=team)
            result[f"team{cnt + 1}_rank"] = team_result.ranking
            cnt += 1

        return result

    def __str__(self):
        return f"Game of {self.session.activity} @ {self.session.datetime}" + \
            f" (Submitter: {self.session.submittor})"


"""
The ranking result of a specific team in a given game.
"""


class Result(SubmittedData):
    game = models.ForeignKey(Game, models.DO_NOTHING)
    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING, related_name="+")
    ranking = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.team} ranked {self.ranking} @ ({self.game})"


"""
A person who forms part of teams to play in games.
"""


class Player(models.Model):
    # id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.TextField()
    email = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "player"

    def to_dict_with_skill(self, activity_id):
        ranks = Ranking.objects.filter(player=self, activity_id=activity_id)
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


"""
A person's current skill ranking for a given activity.
"""


class Ranking(models.Model):
    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "ranking"
        unique_together = (("player", "activity"),)

    def calc_skill(self):
        min_range = 0  # skill_type.min_skill_range
        max_range = 50  # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill

    def __str__(self):
        return f"{self.player} @ {self.activity}: ({self.mu}, {self.sigma})"


"""
A person's historical skill ranking directly after a given game's result.
"""


class SkillHistory(models.Model):
    result = models.ForeignKey(Result, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    activity_id = models.TextField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "skill_history"
        unique_together = (("player", "result"),)

    def calc_skill(self):
        min_range = 0  # skill_type.min_skill_range
        max_range = 50  # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill

    def __str__(self):
        return f"[Game {self.result.game.id}] {self.player} @ " + \
            f"{self.activity_id}: ({self.mu}, {self.sigma})"


"""
A description for the type of skill level that an activity can have.
"""


class SkillType(models.Model):
    id = models.TextField(primary_key=True)
    min_skill_range = models.FloatField(default=0)
    max_skill_range = models.FloatField(default=50)
    initial_mean = models.FloatField(default=25)
    initial_std_dev = models.FloatField(default=25 / 3.0)
    dynamics_factor = models.FloatField(default=25 / 300.0)
    skill_chain = models.FloatField(default=25 / 6.0)
    draw_chance = models.FloatField(default=0.1)

    class Meta:
        db_table = "skill_type"

    def __str__(self):
        return (
            f"Range: {self.min_skill_range}-{self.max_skill_range}, " +
            f"Initial: {self.initial_mean},{self.initial_std_dev}, " +
            f"Skill chain: {self.skill_chain}, Draw: {self.draw_chance}, " +
            f"Dynamics: {self.dynamics_factor}"
        )


"""
A member of an AdhocTeam.
"""


class TeamMember(models.Model):
    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "team_member"
        unique_together = (("player", "team"),)

    def __str__(self):
        return f"{self.player} was member of {self.team}"
