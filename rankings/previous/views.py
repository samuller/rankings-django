"""Django views for this app."""
import json
import time
import socket
import datetime
from typing import List, Dict, Optional, Any, Tuple, cast

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from trueskill import Rating, rate
from django.contrib.auth.decorators import user_passes_test

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from .utils import CsrfExemptSessionAuthentication
from .models import (
    Activity,
    AdhocTeam,
    Player,
    Ranking,
    Game,
    GameSession,
    Result,
    SkillHistory,
    TeamMember,
)


def main_page(request: HttpRequest) -> HttpResponse:
    """Generate the home page that lists all current activities."""
    activities = [
        activity.to_dict_with_url() for activity in Activity.objects.filter(active=True)
    ]
    context = {"player_ids": [], "activities": activities}
    return render(request, "main_page.html", context)


@api_view()
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAdminUser])
def validate_all_matches(request: Request) -> Response:
    """TODO: Validate all outstanding matches."""
    return HttpResponse("")


def activity_summary(request: HttpRequest, activity_url: str) -> HttpResponse:
    """Generata a summary page for an activity (listing recent matches and leading players)."""
    activity = Activity.objects.filter(url=activity_url)
    if len(activity) != 1:
        return redirect("home")
    activity = activity[0].to_dict_with_url()

    active_players_ids = []
    for player in Player.objects.filter(active=True):
        active_players_ids.append([player.id, player.name])

    # active_time_ago = time.mktime((datetime.datetime.now() - datetime.timedelta(days=6*30)).timetuple())
    # active_players_query = Player.objects.filter(
    #     active=True, teammember__team__session__datetime__gt=active_time_ago).distinct()
    all_players = [
        p.to_dict_with_skill(activity["id"]) for p in Player.objects.filter(active=True)
    ]
    all_players.sort(key=lambda pl: pl["skill"], reverse=True)

    top_players = all_players[:5]
    context = {
        "activities": [
            a.to_dict_with_url() for a in Activity.objects.filter(active=True)
        ],
        "activity": activity,
        "players": all_players,
        "active_players": [p for p in top_players],
        "matches": [m.__dict__ for m in GameSession.objects.all().order_by("-id")[:50]],
        "pending_matches": [
            m.to_dict_with_teams()
            for m in Game.objects.filter(
                session__activity=activity["id"], session__validated=None
            ).order_by("-id")
        ],
        "deletable_match_ids": [],
        "player_ids": active_players_ids,
    }
    return render(request, "activity_summary.html", context)


def list_players(
    request: HttpRequest, activity_url: str, sort_by: Optional[str] = None
) -> HttpResponse:
    """List all the players (and their skill) that are active in the given activity."""
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect("home")
    if sort_by is None or len(sort_by) == 0:
        sort_by = "name"

    if sort_by == "skill":
        all_players = [
            p.to_dict_with_skill(activity["id"])
            for p in Player.objects.filter(active=True)
        ]
        all_players.sort(key=lambda pl: pl["skill"], reverse=True)
    else:
        all_players = [
            p.to_dict_with_skill(activity["id"])
            for p in Player.objects.filter(active=True).order_by(sort_by)
        ]

    context = {
        "activities": [
            a.to_dict_with_url() for a in Activity.objects.filter(active=True)
        ],
        "activity": activity,
        "players": [p.__dict__ for p in Player.objects.filter(active=True)],
        "active_players": all_players,
    }
    return render(request, "list_players.html", context)


def player_info(
    request: HttpRequest, activity_url: str, player_id: int
) -> HttpResponse:
    """Generate a summary/profile page for a player in a certain activity."""
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect("home")

    player = Player.objects.get(id=player_id)
    context = {
        "activities": [
            a.to_dict_with_url() for a in Activity.objects.filter(active=True)
        ],
        "activity": activity,
        "player_info": player.to_dict_with_skill(activity["id"]),
        "player_id": player_id,
    }
    return render(request, "player.html", context)


def player_history(
    request: HttpRequest, activity_url: str, player_id: int, max_len: int = 500
) -> HttpResponse:
    """Get the full skill history for a given player and given activity."""
    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return HttpResponse(json.dumps({"skill_history": []}))

    history = SkillHistory.objects.filter(
        player_id=player_id, activity_id=activity.id
    ).order_by("result__datetime")
    # Limit history to last few points
    history = history[max(len(history) - max_len, 0) :]  # noqa: E203
    return HttpResponse(
        json.dumps(
            {
                "skill_history": [
                    {"y": h.calc_skill(), "id": h.result.game.id} for h in history
                ],
            }
        )
    )


def list_matches(
    request: HttpRequest,
    activity_url: str,
    page: int = 1,
    match_id: Optional[int] = None,
) -> HttpResponse:
    """List all the matches for a given activity."""
    page = max(int(page), 1)
    results_per_page = 50
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return HttpResponse(json.dumps({"skill_history": []}))

    players = []
    for player in Player.objects.filter(active=True):
        players.append([player.id, player.name])

    if match_id is None:
        start = (int(page) - 1) * results_per_page
        end = int(page) * results_per_page
        matches = [
            m.to_dict_with_teams()
            for m in Game.objects.filter(
                session__activity__id=activity["id"], session__validated=1
            ).order_by("-id")[start:end]
        ]
    else:
        matches = [Game.objects.get(id=match_id).to_dict_with_teams()]

    total_pages = 1 + (
        Game.objects.filter(
            session__activity__id=activity["id"], session__validated=1
        ).count()
        // results_per_page
    )

    list_pages = [
        val
        for val in range(1, total_pages + 1)
        if val <= 1 or val > (total_pages - 1) or abs(page - val) < 3
    ]
    gaps_idx = [
        idx
        for idx in range(1, len(list_pages))
        if list_pages[idx] - list_pages[idx - 1] > 1
    ]
    for idx in reversed(gaps_idx):
        list_pages.insert(idx, -1)

    pending_matches = [
        m.to_dict_with_teams()
        for m in Game.objects.filter(
            session__activity__id=activity["id"], session__validated=None
        ).order_by("-id")
    ]
    context = {
        "activities": [
            a.to_dict_with_url() for a in Activity.objects.filter(active=True)
        ],
        "activity": activity,
        "player_ids": players,
        "matches": matches,
        "current_page": page,
        "total_pages": total_pages,
        "list_pages": list_pages,
        "pending_matches": pending_matches,
    }
    return render(request, "list_matches.html", context)


@user_passes_test(lambda u: u.is_superuser)
def update(
    request: HttpRequest, activity_url: str, year: Optional[str] = None
) -> HttpResponse:
    """
    Fully clears and recalculates all rankings.

    Requires admin rights as it increases server load.
    """
    activity = Activity.objects.get(url=activity_url)
    if activity is None:
        return HttpResponse("Activity not found.")

    from_date = None
    if year is not None:
        from_date = (int(year), 1, 1)

    start = time.time()
    batch_update_player_skills(activity.id, from_date)
    end = time.time()
    return HttpResponse(f"Update completed in {end - start:.2f}s")


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


def about(request: HttpRequest) -> HttpResponse:
    """Generate the 'about' page."""
    activities = [a.to_dict_with_url() for a in Activity.objects.filter(active=True)]
    context = {"activities": activities}
    return render(request, "about.html", context)


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


@user_passes_test(lambda u: u.is_superuser)
def select_player_to_replace_in_submissions(
    request: HttpRequest, session_ids_str: str
) -> HttpResponse:
    """Generate a view to help select players during the fix of a mistaken submission."""
    session_ids = [int(val) for val in session_ids_str.split(",")]

    team_members = TeamMember.objects.filter(
        team__in=AdhocTeam.objects.filter(session__in=session_ids)
    )
    context = {
        "session_ids": ",".join([str(id) for id in session_ids]),
        "matches": [
            res.summary_str() for res in GameSession.objects.filter(id__in=session_ids)
        ],
        "current_players": [
            val
            for val in Player.objects.filter(
                id__in=team_members.values("player")
            ).values("id", "name")
        ],
        "all_players": Player.objects.all().values("id", "name"),
    }
    return render(request, "select_player_to_fix.html", context)


def new_rating(activity: Activity) -> Rating:
    """Generate a starting ranking for the given activity."""
    # TODO: use activity.skill_ranking
    start_mu = 25
    start_sigma = 25 / 3.0
    return Rating(start_mu, start_sigma)


def generate_blank_ratings(activity: Activity) -> Dict[int, Rating]:
    """Generate an empty dictionary of rankings for all currently known players."""
    ratings = {p.id: new_rating(activity) for p in Player.objects.all()}
    return ratings


def batch_update_player_skills(
    activity_id: int, after_date: Optional[Tuple[int, int, int]] = None
) -> None:
    """Do a full/batch update of player skills for a specific activity.

    This will wipe all current rankings and recalculate them and the SkillHistory's from scratch,
    reconsidering the whole history of games played (or only those after a certain, given, date).
    """
    activity = Activity.objects.get(id=activity_id)
    # Setup initial ratings for each player
    ratings = generate_blank_ratings(activity)

    # We can filter to only consider matches after a given date
    if after_date is None:
        earliest_date = (
            GameSession.objects.filter(activity=activity, validated=1)
            .earliest("datetime")
            .datetime
        )
        after_date_unix = earliest_date
    else:
        after_date_unix = int(time.mktime((*after_date, 0, 0, 0, 0, 0, 0)))

    # Clear skill history that will be reconstructed
    SkillHistory.objects.filter(activity_id=activity_id).delete()

    # Process each match to calculate rating progress and determine final rankings
    incremental_update_player_skills(
        GameSession.objects.filter(
            activity=activity, validated=1, datetime__gte=after_date_unix
        ),
        ratings,
    )


def get_common_activity(game_sessions: List[GameSession]) -> Optional[Activity]:
    """Get the activity in common between a list of GameSessions."""
    activity = game_sessions[0].activity
    # Check that all session are from the same activity
    for session in game_sessions:
        if session.activity.id != activity.id:
            return None
    return cast(Activity, activity)


def incremental_update_player_skills(
    new_game_sessions: Any, current_ratings: Optional[Dict[int, Rating]] = None
) -> Optional[Dict[int, Rating]]:
    """Incrementally update player skills by considering only the given new set of games."""
    if len(new_game_sessions) == 0:
        return current_ratings

    activity = get_common_activity(new_game_sessions)
    assert activity is not None

    if current_ratings is None:
        # Generatings for everyone since some people might not have rankings already
        current_ratings = generate_blank_ratings(activity)
        # Set the values for everyone that already has a ranking
        for ranking in Ranking.objects.filter(activity_id=activity.id):
            assert ranking.player.id in current_ratings
            current_ratings[ranking.player.id] = Rating(ranking.mu, ranking.sigma)

    ratings = current_ratings
    # Process each match (chronologically) to calculate rating progress and determine final rankings
    for session in new_game_sessions.order_by("datetime"):
        teams = AdhocTeam.objects.filter(session=session)

        for game in Game.objects.filter(session=session).order_by(
            "datetime", "position"
        ):
            team_ratings = []
            for team in teams:
                team_members = TeamMember.objects.filter(team=team)
                team_ratings.append(
                    [ratings[member.player.id] for member in team_members]
                )

            results = [Result.objects.get(game=game, team=team) for team in teams]
            team_ratings = rate(
                team_ratings, ranks=[result.ranking for result in results]
            )

            # Update current ratings and save them to SkillHistory
            for idx_team, team in enumerate(teams):
                team_members = TeamMember.objects.filter(team=team)
                for idx_member, member in enumerate(team_members):
                    ratings[member.player.id] = team_ratings[idx_team][idx_member]
                    history = SkillHistory(
                        activity_id=activity.id,
                        result=results[idx_team],
                        player=member.player,
                        mu=team_ratings[idx_team][idx_member].mu,
                        sigma=team_ratings[idx_team][idx_member].sigma,
                    )
                    history.save()
    # Save/update calculated rankings
    for player_id, rating in ratings.items():
        ranking, _ = Ranking.objects.update_or_create(
            activity_id=activity.id,
            player_id=player_id,
            defaults={"mu": rating.mu, "sigma": rating.sigma},
        )
    return ratings


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


def show_id(request: HttpRequest) -> HttpResponse:
@api_view()
    """Return a string to identify the source of the client request."""
    id = identify_request_source(request)
    return HttpResponse(id, content_type="text/plain")


def identify_request_source(request: HttpRequest) -> str:
    """Generate a string that identifies the source of the request."""
    id = str(request.META["REMOTE_ADDR"])
    # Detect nginx ip forwarding
    if "HTTP_X_REAL_IP" in request.META:
        id = str(request.META["HTTP_X_REAL_IP"])
    try:
        # getfqdn() won't throw exception, but then we can't differentiate when it
        # works, and we might generate e.g. "127.0.0.1 (127.0.0.1)"
        # addr = socket.getfqdn(submittor)
        addr = socket.gethostbyaddr(id)
        id = f"{id} ({addr[0]})"
    except:  # noqa: E722
        pass

    return id
