"""Django API views for this app."""

import datetime
import json
import socket
import time
from typing import Any, List, Optional

from django.db.models import ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import Greatest, Least
from django.http import HttpRequest, HttpResponse
from django_filters import BooleanFilter, FilterSet, NumberFilter
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_serializer,
    inline_serializer,
)
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.request import Request
from rest_framework.response import Response

from .models import (
    Activity,
    AdhocTeam,
    Game,
    GameSession,
    Player,
    Ranking,
    Result,
    SkillHistory,
    TeamMember,
)
from .utils import (
    CsrfExemptSessionAuthentication,
    FieldFilterMixin,
    FieldFilterModelSerializer,
    ValidateParamsMixin,
)

# Query parameter to use for filtering fields returned by the serializer.
# We choose to follow PostgREST's "select" convention.
# See: https://postgrest.org/en/stable/references/api/tables_views.html#vertical-filtering
FIELD_FILTER_PARAM = "select"

# We can add a calculated column for "skill" when doing queries on an object that has skill parameters.
# NOTE: Ordering & pagination could get slow for large amounts of data when using calculated columns.
SKILL_EXPRESSION = ExpressionWrapper(
    Greatest(Value(0), Least(Value(50), F("mu") - 3 * F("sigma"))),
    output_field=FloatField(),
)


class ActivitySerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Activities."""

    class Meta:
        model = Activity
        fields = [
            "id",
            "url",
            "name",
            "active",
            "min_teams_per_match",
            "max_teams_per_match",
            "min_players_per_team",
            "max_players_per_team",
            "about",
        ]

    def get_fields(self):
        """Customise the list of fields to serialize."""
        fields = super().get_fields()
        request = self.context.get("request")
        if request:
            # We remove the large "about" field by default, and only return it if you use the field_filter to
            # selectively choose fields and one of them is "about".
            field_filter = request.query_params.get(FIELD_FILTER_PARAM)
            if not field_filter:
                fields.pop("about")
        return fields


@extend_schema(
    parameters=[
        OpenApiParameter(
            "format",
            # We don't set "default" as we prefer if value is unset in API docs.
            description='Format of response to return (defaults to "json").',
            enum=["json", "api"],
        ),
        OpenApiParameter(
            FIELD_FILTER_PARAM,
            description="Subset of fields to return in response (comma separated list).",
        ),
    ]
)
class ActivityViewSet(FieldFilterMixin, ValidateParamsMixin, viewsets.ModelViewSet):
    """API for handling all known activities."""

    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["active"]
    search_fields = ["id", "url", "name"]
    field_filter_param = FIELD_FILTER_PARAM


class PlayerSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Players."""

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "email",
        ]


class PlayerViewSet(FieldFilterMixin, ValidateParamsMixin, viewsets.ModelViewSet):
    """API for handling all known players."""

    queryset = Player.objects.filter(active=True)
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields: List[str] = []
    search_fields = ["name", "email"]


@extend_schema_serializer(exclude_fields=("skill",))
class RankingSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Rankings."""

    activity = ActivitySerializer(fields=["name"])
    player = PlayerSerializer(fields=["id", "name"])
    skill = serializers.ReadOnlyField()

    class Meta:
        model = Ranking
        fields = [
            "activity",
            "player",
            "skill",
            "mu",
            "sigma",
        ]


class RankingViewSet(FieldFilterMixin, ValidateParamsMixin, viewsets.ModelViewSet):
    """API for handling rankings of players per activity."""

    queryset = Ranking.objects.annotate(skill=SKILL_EXPRESSION).filter(player__active=True, skill__gt=0)
    serializer_class = RankingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["activity"]
    search_fields: List[str] = ["skill"]  # "activity.name", "player.name"]
    field_filter_param = FIELD_FILTER_PARAM


class SkillHistoryGameSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Game."""

    class Meta:
        model = Game
        fields = [
            "id",
            "datetime",
            "submittor",
            # "session",
            "position",
        ]


class ResultSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Result."""

    game = SkillHistoryGameSerializer(fields=["id", "datetime", "submittor"])

    class Meta:
        model = Result
        fields = [
            "game",
            "team",
            "ranking",
        ]


@extend_schema_serializer(exclude_fields=("datetime", "game_id", "skill"))
class SkillHistorySerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for SkillHistory."""

    # activity = ActivitySerializer(fields=["name"])
    player = PlayerSerializer(fields=["id", "name"])
    result = ResultSerializer(fields=["game"])
    skill = serializers.ReadOnlyField()
    datetime = serializers.ReadOnlyField()
    game_id = serializers.ReadOnlyField()

    class Meta:
        model = SkillHistory
        fields = [
            "activity_id",
            "datetime",
            "game_id",
            "player",
            "result",
            "skill",
            "mu",
            "sigma",
        ]


class SkillHistoryViewSet(FieldFilterMixin, ValidateParamsMixin, viewsets.ModelViewSet):
    """API for handling the historical record of a player's skill over time (per activity)."""

    queryset = SkillHistory.objects.annotate(skill=SKILL_EXPRESSION).filter(player__active=True)
    serializer_class = SkillHistorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["activity_id", "player"]
    search_fields: List[str] = []
    field_filter_param = FIELD_FILTER_PARAM

    def get_queryset(self):
        """Get the list of items for this view."""
        base_query = super().get_queryset()
        activity_url = self.kwargs["activity_url"]
        player_id = self.kwargs["player_id"]
        return base_query.filter(activity_id=activity_url, player__id=player_id).annotate(
            datetime=F("result__game__datetime"), game_id=F("result__game__id")
        )


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for TeamMember."""

    player = PlayerSerializer()

    class Meta:
        model = TeamMember
        fields = ["player"]


class AdhocTeamSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for AdhocTeam."""

    members = TeamMemberSerializer(source="teammember_set", many=True, read_only=True)

    class Meta:
        model = AdhocTeam
        fields = ["id", "members"]


@extend_schema_serializer(exclude_fields=("winning_team",))
class MatchGameSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Game."""

    # results = MatchResultSerializer(source="result_set", many=True, read_only=True)
    winning_team = serializers.SerializerMethodField("find_winning_team")

    class Meta:
        model = Game
        fields = [
            "id",
            "datetime",
            "submittor",
            "position",
            # "results",
            "winning_team",
        ]

    def find_winning_team(self, game) -> int:
        """Fetch ID of team with rank of 1 in the current game."""
        return Result.objects.filter(game=game, ranking=1).first().team.id


class MatchSerializer(serializers.HyperlinkedModelSerializer, FieldFilterModelSerializer):
    """Serializer for Matches (a GameSet of multiple Games)."""

    games = MatchGameSerializer(source="game_set", many=True, read_only=True)
    teams = AdhocTeamSerializer(source="adhocteam_set", many=True, read_only=True)

    class Meta:
        model = GameSession
        fields = [
            "id",
            "datetime",
            "submittor",
            "validated",
            "games",
            "teams",
        ]


class MatchFilter(FilterSet):
    """Filter used to select matches on specified fields."""

    validated = NumberFilter(field_name="validated")
    pending = BooleanFilter(field_name="validated", lookup_expr="isnull")


class MatchViewSet(FieldFilterMixin, ValidateParamsMixin, viewsets.ModelViewSet):
    """API for handling matches (potentially a set of multiple games) per activity."""

    queryset = GameSession.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = MatchFilter
    filterset_fields = ["validated", "pending"]
    search_fields: List[str] = ["submittor"]
    field_filter_param = FIELD_FILTER_PARAM

    def get_queryset(self):
        """Get the list of items for this view."""
        base_query = super().get_queryset()
        activity_url = self.kwargs["activity_url"]
        return base_query.filter(activity_id=activity_url)


@extend_schema(request=None, responses=None, auth=[])
@api_view()
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAdminUser])
def validate_all_matches(request: Request) -> Response:
    """TODO: Validate all outstanding matches."""
    return HttpResponse("")


class ValidReasonSerializer(serializers.Serializer):
    """A general result to say if processing was successful, and if not give a reason."""

    valid = serializers.BooleanField()
    reason = serializers.CharField()


@extend_schema(
    request=inline_serializer("MatchID", fields={"match-id": serializers.IntegerField()}),
    responses=ValidReasonSerializer,
)
@api_view(["POST"])
def undo_submit(request: Request, activity_url: str) -> Response:
    """
    (Not yet implemented) API to undo submitted matches.

    TODO: Allow a user to undo their own mistaken submission (within some constraints).
    """
    submittor = identify_request_source(request)

    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return gen_valid_reason_response(valid=False, reason="Activity not found")

    if request.method != "POST":
        return gen_valid_reason_response(valid=False, reason="Only POST supported")

    json_data = json.loads(request.body.decode("utf-8"))
    match_id = json_data["match-id"]
    try:
        game = Game.objects.get(id=match_id)
    except Game.DoesNotExist:
        return gen_valid_reason_response(valid=False, reason=f"Match not found: {match_id}")

    if game.session.submittor != submittor:
        return gen_valid_reason_response(valid=False, reason="Only the original submittor can delete their submission")

    # TODO: use UTC?
    expiry_time = datetime.datetime.fromtimestamp(game.session.datetime).astimezone() + datetime.timedelta(minutes=15)
    if datetime.datetime.now().astimezone() >= expiry_time:
        return gen_valid_reason_response(
            valid=False, reason="Submission undo period has expired. It can no longer be altered."
        )

    game.delete()

    return gen_valid_reason_response(valid=True, reason="Match {match_id} deleted")


def gen_valid_reason_response(valid: bool, reason: str) -> HttpResponse:  # noqa: FBT001
    """Help to generate a JSON message providing feedback on the submission process."""
    return HttpResponse(json.dumps({"valid": valid, "reason": reason}))


@extend_schema(
    request=inline_serializer(
        "SubmitMatchResults",
        fields={
            # Teams (list of player IDs) per match
            "teams": serializers.ListField(  # matches
                child=serializers.ListField(  # teams
                    child=serializers.ListField(child=serializers.IntegerField())  # players
                )
            ),
            # Winning team ID per match
            "wins": serializers.ListField(child=serializers.IntegerField()),
        },
    ),
    responses=ValidReasonSerializer,
)
@api_view(["POST"])
@authentication_classes([])
def submit_match(request: Request, activity_url: str) -> Response:
    """
    Submit or record one or more matches.

    Parameters
    ----------
    - **teams**:
        An array of teams which are each specified as an array of player ids.
    - **wins**:
        An array of which team won each game, specified with team indexes (1-indexed).
    """
    submittor = identify_request_source(request)

    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return gen_valid_reason_response(valid=False, reason="Activity not found")

    if request.method != "POST":
        return gen_valid_reason_response(valid=False, reason="Only POST supported")

    json_data = json.loads(request.body.decode("utf-8"))

    teams_per_match = json_data["teams"]
    all_teams = [team for match_teams in teams_per_match for team in match_teams]
    winning_teams = json_data["wins"]

    # Look for the first empty team (else set to None)
    invalid_team = next((team for team in all_teams if len(team) == 0), None)
    if len(all_teams) == 0 or invalid_team is not None:
        return gen_valid_reason_response(valid=False, reason="Invalid teams")

    # Look for the first negative player id (else set to None)
    invalid_player = next((player for team in all_teams for player in team if player < 0), None)
    if invalid_player is not None:
        return gen_valid_reason_response(valid=False, reason="Invalid player ids")

    result_ids = record_matches(activity, teams_per_match, winning_teams, submittor=submittor)
    # ip = request.environ['REMOTE_ADDR']
    # set_deletable_matches(result_ids)

    # JSON object returned should identify whether submission succeeded and
    # help locate any issues in the form
    if result_ids is None:
        return gen_valid_reason_response(valid=False, reason="Submission failed")
    return gen_valid_reason_response(valid=True, reason="")


@extend_schema(
    request=inline_serializer(
        "ReplacePlayer",
        fields={
            "prev_player_id": serializers.IntegerField(),
            "new_player_id": serializers.IntegerField(),
        },
    ),
    responses=OpenApiTypes.STR,
    auth=[],
)
@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAdminUser])
def replace_player_in_submissions(request: Request) -> Response:
    """Correct a mistaken submission by replacing an incorrectly selected player."""
    if request.method != "POST":
        return HttpResponse("Not POST!", content_type="text/plain")

    session_ids = [int(id) for id in request.POST.get("session_ids").split(",")]
    prev_player_id = request.POST["prev_player_id"]
    new_player_id = request.POST["new_player_id"]

    team_members = TeamMember.objects.filter(team__in=AdhocTeam.objects.filter(session__in=session_ids))

    count_changed = team_members.filter(player=Player.objects.get(id=prev_player_id)).update(
        player=Player.objects.get(id=new_player_id)
    )
    return HttpResponse(
        f"Successfully changed {count_changed} submissions",
        content_type="text/plain",
    )


# Logic for saving matches
def record_matches(
    activity: Activity,
    teams_per_match: List[List[List[int]]],
    winning_team_per_match: List[int],
    submittor: str,
    submission_time: Optional[int] = None,
) -> Optional[List[int]]:
    """Record multiple matches for a single activity."""
    if len(teams_per_match) != len(winning_team_per_match):
        raise ValueError("Per-match lists should have the same length")
    results = []

    for i in range(len(teams_per_match)):
        if submission_time is None:
            submission_time = int(time.time())
        session = GameSession(activity=activity, datetime=submission_time, submittor=submittor)
        session.save()

        winning_team = winning_team_per_match[i]
        team = teams_per_match[i]
        result_id = record_match(session, team, int(winning_team))
        if result_id is None:
            # TODO: invalidate/rollback whole list of matches!
            return None
        results.append(result_id)
    return results


def record_match(session: GameSession, teams: List[List[int]], winning_team: int) -> Optional[Any]:
    """Record a single match as part of the given GameSession."""
    # TODO: support any number of teams (2+)
    if winning_team == 1:
        rankings = [1, 2]
    elif winning_team == 2:  # noqa: PLR2004
        rankings = [2, 1]
    else:
        raise AssertionError(f"Winner incorrectly identified: {winning_team}")

    submit_time = int(time.time())
    game = Game.objects.create(datetime=submit_time, submittor=session.submittor, session=session, position=0)

    for i, team in enumerate(teams):
        if len(team) == 0:
            session.validated = False
            session.save()
            return None

        adhoc_team = AdhocTeam(session=session)
        adhoc_team.save()

        _ = Result.objects.create(
            datetime=submit_time,
            submittor=session.submittor,
            game=game,
            team=adhoc_team,
            ranking=rankings[i],
        )

        for player_id in team:
            # exit on invalid player
            if player_id < 0:
                session.validated = False
                session.save()
                return None
            player = Player.objects.get(id=player_id)

            member = TeamMember(team=adhoc_team, player=player)
            member.save()

    return session.id


@extend_schema(
    request=None,
    responses=inline_serializer(
        "SourceID",
        fields={
            "source": serializers.CharField(),
        },
    ),
)
@api_view()
def show_source_id(request: Request) -> Response:
    """Return a string to identify the source of the client request."""
    src = identify_request_source(request)
    return Response({"source": src})


def identify_request_source(request: HttpRequest) -> str:
    """Generate a string that identifies the source of the request."""
    src = str(request.META["REMOTE_ADDR"])
    # Detect nginx ip forwarding
    if "HTTP_X_REAL_IP" in request.META:
        src = str(request.META["HTTP_X_REAL_IP"])
    elif "HTTP_X_FORWARDED_FOR" in request.META:
        src = str(request.META["HTTP_X_FORWARDED_FOR"])
    try:
        # getfqdn() won't throw exception, but then we can't differentiate when it
        # works, and we might generate e.g. "127.0.0.1 (127.0.0.1)"
        # addr = socket.getfqdn(submittor)
        addr = socket.gethostbyaddr(src)
        src = f"{src} ({addr[0]})"
    except:  # noqa: E722,S110
        pass

    return src
