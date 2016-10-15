from django.db import models

# Create your models here.


class Player(models.Model):
    name = models.TextField()
    email = models.TextField()

    class Meta:
        db_table = "player"
        # managed = False


class SkillType(models.Model):
    min_skill_range = models.FloatField(default=0.0)
    max_skill_range = models.FloatField(default=50.0)
    initial_mean = models.FloatField(default=25.0)
    initial_std_dev = models.FloatField(default=25/3.0)
    dynamics_factor = models.FloatField(default=(25/3.0)/100.0)
    skill_chain = models.FloatField(default=25/6.0)
    draw_chance = models.FloatField(default=0.1)

    class Meta:
        db_table = "skill_type"


class Activity(models.Model):
    name = models.CharField(max_length=64)
    skill_type = models.ForeignKey(SkillType)
    min_teams_per_match = models.IntegerField(default=1)
    max_teams_per_match = models.IntegerField(null=True)
    min_players_per_team = models.IntegerField(default=1)
    max_players_per_team = models.IntegerField(default=1, null=True)
    about = models.TextField()

    class Meta:
        db_table = "activity"


class Ranking(models.Model):
    activity = models.ForeignKey(Activity)
    player = models.ForeignKey(Player)
    active = models.BooleanField()
    mu = models.FloatField()
    sigma = models.FloatField()

    class Meta:
        db_table = "ranking"


class Result(models.Model):
    activity = models.ForeignKey(Activity)
    validated = models.IntegerField()
    submittor = models.CharField(max_length=255)
    datetime = models.DateTimeField()

    class Meta:
        db_table = "result"


class ResultSet(models.Model):
    pass

    class Meta:
        db_table = "result_set"


class ResultSetMember(models.Model):
    result_set = models.ForeignKey(ResultSet)
    result = models.ForeignKey(Result)

    class Meta:
        db_table = "result_set_member"


class AdhocTeam(models.Model):
    result = models.ForeignKey(Result)
    ranking = models.IntegerField()

    class Meta:
        db_table = "adhoc_team"


class TeamMember(models.Model):
    team = models.ForeignKey(AdhocTeam)
    player = models.ForeignKey(Player)
    validate = models.IntegerField()

    class Meta:
        db_table = "team_member"


class SkillHistory(models.Model):
    result = models.ForeignKey(Result)
    player = models.ForeignKey(Player)
    activity = models.ForeignKey(Activity)
    mu = models.FloatField()
    sigma = models.FloatField()

    class Meta:
        db_table = "skill_history"
