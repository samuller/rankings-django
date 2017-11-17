import json
import time

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from trueskill import Rating, rate
from django.contrib.auth.decorators import user_passes_test

from .models import *


# Create your views here.


def main_page(request):
    activities = [activity.to_dict_with_url() for activity in Activity.objects.all()]
    context = {'player_ids': [], 'activities': activities}
    return render(request, 'main_page.html', context)


def validate_all_matches(request):
    return HttpResponse("")


def activity_summary(request, activity_url):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect('home')

    active_players = []
    for player in Player.objects.filter(active=True):
        active_players.append([player.id, player.name])

    all_players = [p.to_dict_with_skill(activity["id"]) for p in Player.objects.filter(active=True)]
    all_players.sort(key=lambda pl: pl["skill"], reverse=True)
    top_players = all_players[:5]
    context = {
        'activities': activities,
        'activity': activity,
        'players': all_players,
        'active_players': [p for p in top_players],
        'matches': [m.__dict__ for m in GameSession.objects.all().order_by('-id')[:50]],
        'pending_matches': [m.to_dict_with_teams() for m in
                            Game.objects.filter(session__activity=activity_url, session__validated=None)
                            .order_by('-id')
                            ],
        'deletable_match_ids': [],
        'player_ids': active_players
    }
    return render(request, 'activity_summary.html', context)


def list_players(request, activity_url, sort_by):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect('home')

    if sort_by == "skill":
        all_players = [p.to_dict_with_skill(activity["id"]) for p in Player.objects.filter(active=True)]
        all_players.sort(key=lambda pl: pl["skill"], reverse=True)
    else:
        all_players = [p.to_dict_with_skill(activity["id"]) for p in Player.objects.filter(active=True).order_by(sort_by)]

    context = {
        'activities': activities,
        'activity': activity,
        'players': [p.__dict__ for p in Player.objects.filter(active=True)],
        'active_players': all_players,
    }
    return render(request, 'list_players.html', context)


def player_info(request, activity_url, player_id):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect('home')

    player = Player.objects.get(id=player_id)
    context = {
        'activities': activities,
        'activity': activity,
        'player_info': player.to_dict_with_skill(activity_url),
        'player_id': player_id,
    }
    return render(request, 'player.html', context)


def player_history(request, activity_url, player_id, max_len=500):
    activity = Activity.objects.get(id=activity_url)
    if activity is None:
        return HttpResponse(json.dumps({'skill_history': []}))

    history = SkillHistory.objects.filter(player_id=player_id, activity_id=activity_url)\
        .order_by('result__datetime')
    # Limit history to last few points
    history = history[max(len(history)-max_len, 0):]
    return HttpResponse(json.dumps({
        'skill_history': [
            {'y': h.calc_skill(), 'id': h.result.game.id} for h in history],
    }))


def list_matches(request, activity_url, page=1, match_id=None):
    page = max(int(page), 1)
    results_per_page = 50
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return HttpResponse(json.dumps({'skill_history': []}))

    players = []
    for player in Player.objects.filter(active=True):
        players.append([player.id, player.name])

    if match_id is None:
        start = (int(page)-1) * results_per_page
        end = int(page) * results_per_page
        matches = [m.to_dict_with_teams() for m in
                   Game.objects.filter(session__activity__id=activity_url, session__validated=1)
                       .order_by('-id')[start:end]]
    else:
        matches = [Game.objects.get(id=match_id).to_dict_with_teams()]

    total_pages = 1 + (Game.objects.filter(session__activity__id=activity_url, session__validated=1).count() //
                       results_per_page)

    list_pages = [val for val in range(1, total_pages + 1) if val <= 1 or val > (total_pages - 1) or abs(page - val) < 3]
    gaps_idx = [idx for idx in range(1, len(list_pages)) if list_pages[idx] - list_pages[idx-1] > 1]
    for idx in reversed(gaps_idx):
        list_pages.insert(idx, -1)

    pending_matches = [m.to_dict_with_teams() for m in
                       Game.objects
                           .filter(session__activity__id=activity_url, session__validated=None)
                           .order_by('-id')]
    context = {
        'activities': activities,
        'activity': activity,
        'player_ids': players,
        'matches': matches,
        'current_page': page,
        'total_pages': total_pages,
        'list_pages': list_pages,
        'pending_matches': pending_matches,
    }
    return render(request, 'list_matches.html', context)


@user_passes_test(lambda u: u.is_superuser)
def update(request, activity_url):
    """
    Fully clears and recalculates all rankings.
    
    Requires admin rights as it increases server load.
    """
    activity = Activity.objects.get(id=activity_url)
    if activity is None:
        return HttpResponse("Activity not found.")

    start = time.time()
    batch_update_player_skills(activity.id)
    end = time.time()
    return HttpResponse("Update completed in %.2fs" % (end - start))


def get_players(request, activity_url):
    return HttpResponse("")


@csrf_exempt
def submit_match(request, activity_url):
    submittor = request.META['REMOTE_ADDR']
    # Detect nginx ip forwarding
    if 'HTTP_X_REAL_IP' in request.META:
        submittor = request.META['HTTP_X_REAL_IP']

    def gen_valid_reason_response(valid, reason):
        return HttpResponse(json.dumps({'valid': valid, 'reason': reason}))

    activity = Activity.objects.get(id=activity_url)
    if activity is None:
        return gen_valid_reason_response(False, 'Activity not found')

    if request.method != "POST":
        return gen_valid_reason_response(False, 'Only POST supported')

    json_data = json.loads(request.body.decode('utf-8'))

    teams_per_match = json_data['teams']
    all_teams = [team for match_teams in teams_per_match for team in match_teams]
    winning_teams = json_data["wins"]

    # Look for the first empty team (else set to None)
    invalid_team = next((team for team in all_teams if len(team) == 0), None)
    if invalid_team is not None:
        return gen_valid_reason_response(False, 'Invalid teams')

    # Look for the first negative player id (else set to None)
    invalid_player = next((player for team in all_teams for player in team if player < 0), None)
    if invalid_player is not None:
        return gen_valid_reason_response(False, 'Invalid player ids')

    activity = Activity.objects.get(id=activity_url)
    result_ids = record_matches(
            activity,
            teams_per_match,
            winning_teams,
            submittor=submittor)
    # ip = request.environ['REMOTE_ADDR']
    # set_deletable_matches(result_ids)

    # JSON object returned should identify whether submission succeeded and
    # help locate any issues in the form
    if result_ids is None:
        return gen_valid_reason_response(False, 'Submission failed')
    else:
        return gen_valid_reason_response(True, '')


def about(request):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    context = {
        'activities': activities
    }
    return render(request, 'about.html', context)


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def replace_player_in_submissions(request):
    if request.method != "POST":
        return HttpResponse("Not POST!", content_type='text/plain')

    session_ids = [int(id) for id in request.POST.get("session_ids").split(",")]
    prev_player_id = request.POST["prev_player_id"]
    new_player_id = request.POST["new_player_id"]

    team_members = TeamMember.objects.filter(team__in=
      AdhocTeam.objects.filter(session__in=session_ids))
    players = set([m.player for m in team_members])

    count_changed = (team_members
      .filter(player=Player.objects.get(id=prev_player_id))
      .update(player=Player.objects.get(id=new_player_id))
    )
    return HttpResponse("Successfully changed %s submissions" % (count_changed,),
      content_type='text/plain')


@user_passes_test(lambda u: u.is_superuser)
def select_player_to_replace_in_submissions(request, session_ids_str):
    session_ids = [int(val) for val in session_ids_str.split(",")]

    team_members = TeamMember.objects.filter(team__in=
      AdhocTeam.objects.filter(session__in=session_ids))
    players = set([m.player for m in team_members])
    context = {
      'session_ids': ",".join([str(id) for id in session_ids]),
      'matches': [res.summary_str() for res in GameSession.objects.filter(id__in=session_ids)],
      'current_players': [val for val in
          Player.objects.filter(id__in=team_members.values('player')).values('id', 'name')],
      'all_players': Player.objects.all().values('id', 'name')}
    return render(request, 'select_player_to_fix.html', context)


def batch_update_player_skills(activity_id):
    activity = Activity.objects.get(id=activity_id)

    # Clear skill history that will be reconstructed
    SkillHistory.objects.filter(activity_id=activity_id).delete()

    # Setup initial ratings for each player
    start_mu = 25
    start_sigma = 25 / 3.0
    ratings = {p.id: Rating(start_mu, start_sigma) for p in Player.objects.all()}

    # Process each match to calculate rating progress and determine final rankings
    for session in GameSession.objects.filter(activity=activity, validated=1):
        teams = AdhocTeam.objects.filter(session=session)

        for game in Game.objects.filter(session=session):
            team_ratings = []
            for team in teams:
                team_members = TeamMember.objects.filter(team=team)
                team_ratings.append([ratings[member.player.id] for member in team_members])

            results = [Result.objects.get(game=game, team=team) for team in teams]
            team_ratings = rate(team_ratings, ranks=[result.ranking for result in results])

            # Update current ratings and save them to SkillHistory
            for idx_team, team in enumerate(teams):
                team_members = TeamMember.objects.filter(team=team)
                for idx_member, member in enumerate(team_members):
                    ratings[member.player.id] = team_ratings[idx_team][idx_member]
                    history = SkillHistory(activity_id=activity_id, result=results[idx_team],
                                           player=member.player,
                                           mu=team_ratings[idx_team][idx_member].mu,
                                           sigma=team_ratings[idx_team][idx_member].sigma)
                    history.save()

    # Save calculated rankings
    Ranking.objects.filter(activity_id=activity_id).delete()
    for player_id in ratings:
        rating = ratings[player_id]
        ranking = Ranking(activity_id=activity_id, player_id=player_id,
                          mu=rating.mu, sigma=rating.sigma)
        ranking.save()


# Logic for saving matches
def record_matches(activity, teams_per_match, winning_team_per_match, submittor, submission_time=None):
    assert len(teams_per_match) == len(winning_team_per_match)
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


def record_match(session, teams, winning_team):
    # TODO: support any number of teams (2+)
    if winning_team == 1:
        rankings = [1, 2]
    elif winning_team == 2:
        rankings = [2, 1]
    else:
        assert False, "Winner incorrectly identified: %s" % winning_team

    submit_time = int(time.time())
    game = Game.objects.create(
        datetime=submit_time,
        submittor=session.submittor,
        session=session,
        position=0
    )

    for i, team in enumerate(teams):
        if len(team) == 0:
            session.validated = False
            session.save()
            return None

        adhoc_team = AdhocTeam(session=session)
        adhoc_team.save()

        result = Result.objects.create(
            datetime=submit_time,
            submittor=session.submittor,
            game=game, team=adhoc_team,
            ranking=rankings[i]
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

