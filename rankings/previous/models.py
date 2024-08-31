#!/usr/bin/env python3
"""
Django ORM database models.

Originally generated with `inspectdb`.
> This is an auto-generated Django model module.
> You'll have to do the following manually to clean this up:
>   * Rearrange models' order
>   * Make sure each model has one field with primary_key=True
>   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
> Feel free to rename the models, but don't rename db_table values or field names.
"""

from __future__ import unicode_literals

import datetime

from django.db import models

from .utils import cardinal_to_ordinal


class Activity(models.Model):
    """A type of activity/game for which new match results can be recorded."""

    id = models.TextField(primary_key=True)
    url = models.TextField(unique=True, blank=False, null=False)
    name = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)
    skill_type = models.ForeignKey("SkillType", models.DO_NOTHING, db_column="skill_type", blank=True, null=True)
    min_teams_per_match = models.IntegerField(default=2)
    max_teams_per_match = models.IntegerField(blank=True, null=True)
    min_players_per_team = models.IntegerField(default=1)
    max_players_per_team = models.IntegerField(blank=True, null=True, default=1)
    about = models.TextField(blank=True, default="")

    class Meta:
        db_table = "activity"

    def __str__(self):
        return self.name

    def to_dict_with_url(self):
        """Convert whole object to a dictionary."""
        result = self.__dict__
        # TODO: no longer "with_url"
        # result["url"] = result["id"]
        return result


class SubmittedData(models.Model):
    """An abstract class for objects for recording how data was submitted."""

    datetime = models.IntegerField(blank=True, null=True)
    submittor = models.TextField(blank=True, default="")

    class Meta:
        abstract = True


class GameSession(SubmittedData):
    """A group of games played together in one session.

    More specifically, games played with the same players, at the same location, within a certain
    period of time (see Game).
    """

    # id = models.IntegerField(primary_key=True)  # AutoField?
    activity = models.ForeignKey(Activity, models.DO_NOTHING, null=True)
    # Null = unvalidated, True = validated, False = invalidated
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "gamesession"

    def __str__(self):
        return f"Game of {self.activity} @ {self.datetime} (Submitter: {self.submittor})"

    def get_ranked_teams(self):
        """Generate the list of teams involved in the session, orderd by their resulting ranking."""
        return [team for team in AdhocTeam.objects.filter(result=self).order_by("ranking")]

    def summary_str(self):
        """Generate string summarising game session details."""
        result_str = ", ".join(
            [
                f"{cardinal_to_ordinal(Result.objects.get(team=team).ranking)}: {team.members_str()}"
                for team in AdhocTeam.objects.filter(session=self)
            ]
        )
        return f"[{self.id}] {self.activity.id} result: {result_str}"


class AdhocTeam(models.Model):
    """A group of players that formed a team for a session (see TeamMember)."""

    session = models.ForeignKey(GameSession, models.DO_NOTHING, null=True)

    class Meta:
        db_table = "adhoc_team"

    def __str__(self):
        return f"Team {self.id}"

    def members_str(self):
        """Generate a text summary of players in team."""
        members = [str(m.player) for m in TeamMember.objects.filter(team=self)]
        if len(members) == 0:
            return ""
        if len(members) == 1:
            return members[0]
        return ", ".join(members[:-1]) + " & " + members[-1]


class Game(SubmittedData):
    """A single game played within a session."""

    session = models.ForeignKey(GameSession, models.DO_NOTHING)
    position = models.IntegerField(default=0)

    def __str__(self):
        return f"Game of {self.session.activity} @ {self.session.datetime} (Submitter: {self.session.submittor})"

    def summary_str_2(self):
        """Generate string summarising the game result."""
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
        """Get game as well as team details as a dict."""
        result = self.__dict__
        # TODO: use UTC?
        result["relative_date"] = datetime.datetime.fromtimestamp(self.datetime).astimezone()
        result["date"] = datetime.datetime.fromtimestamp(self.datetime).astimezone()
        teams = AdhocTeam.objects.filter(session=self.session)
        for idx, team in enumerate(teams):
            result[f"team{idx + 1}"] = team.members_str()
            team_result = Result.objects.get(game=self, team=team)
            result[f"team{idx + 1}_rank"] = team_result.ranking

        return result


class Result(SubmittedData):
    """The ranking result of a specific team in a given game."""

    game = models.ForeignKey(Game, models.DO_NOTHING)
    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING, related_name="+")
    ranking = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.team} ranked {self.ranking} @ ({self.game})"


class Player(models.Model):
    """A person who forms part of teams to play in games."""

    # id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.TextField()
    email = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "player"

    def __str__(self):
        return self.name

    def to_dict_with_skill(self, activity_id):
        """Get player's skill as dict containing ranking and skill probabilities."""
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


class Ranking(models.Model):
    """A person's current skill ranking for a given activity."""

    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "ranking"
        unique_together = (("player", "activity"),)

    def __str__(self):
        return f"{self.player} @ {self.activity}: ({self.mu}, {self.sigma})"

    def calc_skill(self) -> float:
        """Calculate ranking/skill value from skill probability."""
        min_range = 0  # TODO: skill_type.min_skill_range
        max_range = 50  # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill


class SkillHistory(models.Model):
    """A person's historical skill ranking directly after a given game's result."""

    result = models.ForeignKey(Result, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    mu = models.FloatField(blank=True, null=True)
    sigma = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "skill_history"
        unique_together = (("player", "result"),)

    def __str__(self):
        return f"[Game {self.result.game.id}] {self.player} @ {self.activity}: ({self.mu}, {self.sigma})"

    def calc_skill(self):
        """Calculate ranking/skill value from skill probability."""
        min_range = 0  # TODO: skill_type.min_skill_range
        max_range = 50  # skill_type.max_skill_range

        skill = max(min_range, min(self.mu - 3 * self.sigma, max_range))
        return skill


class SkillType(models.Model):
    """A description for the type of skill level that an activity can have."""

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
            f"Range: {self.min_skill_range}-{self.max_skill_range}, "
            + f"Initial: {self.initial_mean},{self.initial_std_dev}, "
            + f"Skill chain: {self.skill_chain}, Draw: {self.draw_chance}, "
            + f"Dynamics: {self.dynamics_factor}"
        )


class TeamMember(models.Model):
    """A member of an AdhocTeam."""

    team = models.ForeignKey(AdhocTeam, models.DO_NOTHING)
    player = models.ForeignKey(Player, models.DO_NOTHING)
    validated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "team_member"
        unique_together = (("player", "team"),)

    def __str__(self):
        return f"{self.player} was member of {self.team}"
