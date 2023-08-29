"""Django API views for this app."""
import json
import time
import socket
import datetime
from typing import List, Optional, Any

from django.http import HttpResponse, HttpRequest
from django.core.exceptions import FieldDoesNotExist
from rest_framework import permissions, serializers, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.settings import api_settings

from .utils import CsrfExemptSessionAuthentication
from .models import (
    Activity,
    AdhocTeam,
    Player,
    Game,
    GameSession,
    Result,
    TeamMember,
)


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
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
        ]


class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Activities."""

    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["active"]

    def get_queryset(self):
        """Get the list of items for this view."""
        # Check for invalid query parameters.
        allowed_params = [api_settings.URL_FORMAT_OVERRIDE, *self.filterset_fields]
        if not set(self.request.GET.keys()).issubset(allowed_params):
            invalid_params = list(set(self.request.GET.keys()) - set(allowed_params))
            raise FieldDoesNotExist(f"Invalid parameter: {invalid_params}")

        return Activity.objects.all()


@api_view()
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAdminUser])
def validate_all_matches(request: Request) -> Response:
    """TODO: Validate all outstanding matches."""
    return HttpResponse("")


@api_view()
def get_players(request: Request, activity_url: str) -> Response:
    """TODO: Get all players for an activity (currently embedded in page HTML)."""
    return HttpResponse("")


@api_view(["POST"])
def undo_submit(request: Request, activity_url: str) -> Response:
    """TODO: Allow a user to undo their own mistaken submission (within some constraints)."""
    submittor = identify_request_source(request)

    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return gen_valid_reason_response(False, "Activity not found")

    if request.method != "POST":
        return gen_valid_reason_response(False, "Only POST supported")

    json_data = json.loads(request.body.decode("utf-8"))
    match_id = json_data["match-id"]
    try:
        game = Game.objects.get(id=match_id)
    except Game.DoesNotExist:
        return gen_valid_reason_response(False, f"Match not found: {match_id}")

    if game.session.submittor != submittor:
        return gen_valid_reason_response(
            False, "Only the original submittor can delete their submission"
        )

    expiry_time = datetime.datetime.fromtimestamp(
        game.session.datetime
    ) + datetime.timedelta(minutes=15)
    if datetime.datetime.now() >= expiry_time:
        return gen_valid_reason_response(
            False, "Submission undo period has expired. It can no longer be altered."
        )

    game.delete()

    return gen_valid_reason_response(True, "Match {match_id} deleted")


def gen_valid_reason_response(valid: bool, reason: str) -> HttpResponse:
    """Help to generate a JSON message providing feedback on the submission process."""
    return HttpResponse(json.dumps({"valid": valid, "reason": reason}))


@api_view(["POST"])
@authentication_classes([])
def submit_match(request: Request, activity_url: str) -> Response:
    """View to submit and record one or matches."""
    submittor = identify_request_source(request)

    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return gen_valid_reason_response(False, "Activity not found")

    if request.method != "POST":
        return gen_valid_reason_response(False, "Only POST supported")

    json_data = json.loads(request.body.decode("utf-8"))

    teams_per_match = json_data["teams"]
    all_teams = [team for match_teams in teams_per_match for team in match_teams]
    winning_teams = json_data["wins"]

    # Look for the first empty team (else set to None)
    invalid_team = next((team for team in all_teams if len(team) == 0), None)
    if len(all_teams) == 0 or invalid_team is not None:
        return gen_valid_reason_response(False, "Invalid teams")

    # Look for the first negative player id (else set to None)
    invalid_player = next(
        (player for team in all_teams for player in team if player < 0), None
    )
    if invalid_player is not None:
        return gen_valid_reason_response(False, "Invalid player ids")

    result_ids = record_matches(
        activity, teams_per_match, winning_teams, submittor=submittor
    )
    # ip = request.environ['REMOTE_ADDR']
    # set_deletable_matches(result_ids)

    # JSON object returned should identify whether submission succeeded and
    # help locate any issues in the form
    if result_ids is None:
        return gen_valid_reason_response(False, "Submission failed")
    else:
        return gen_valid_reason_response(True, "")


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

    team_members = TeamMember.objects.filter(
        team__in=AdhocTeam.objects.filter(session__in=session_ids)
    )

    count_changed = team_members.filter(
        player=Player.objects.get(id=prev_player_id)
    ).update(player=Player.objects.get(id=new_player_id))
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
    assert len(teams_per_match) == len(winning_team_per_match)
    results = []

    for i in range(len(teams_per_match)):
        if submission_time is None:
            submission_time = int(time.time())
        session = GameSession(
            activity=activity, datetime=submission_time, submittor=submittor
        )
        session.save()

        winning_team = winning_team_per_match[i]
        team = teams_per_match[i]
        result_id = record_match(session, team, int(winning_team))
        if result_id is None:
            # TODO: invalidate/rollback whole list of matches!
            return None
        results.append(result_id)
    return results


def record_match(
    session: GameSession, teams: List[List[int]], winning_team: int
) -> Optional[Any]:
    """Record a single match as part of the given GameSession."""
    # TODO: support any number of teams (2+)
    if winning_team == 1:
        rankings = [1, 2]
    elif winning_team == 2:
        rankings = [2, 1]
    else:
        assert False, f"Winner incorrectly identified: {winning_team}"

    submit_time = int(time.time())
    game = Game.objects.create(
        datetime=submit_time, submittor=session.submittor, session=session, position=0
    )

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
    try:
        # getfqdn() won't throw exception, but then we can't differentiate when it
        # works, and we might generate e.g. "127.0.0.1 (127.0.0.1)"
        # addr = socket.getfqdn(submittor)
        addr = socket.gethostbyaddr(src)
        src = f"{src} ({addr[0]})"
    except:  # noqa: E722
        pass

    return src
