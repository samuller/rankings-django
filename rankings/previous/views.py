import json
import time

from django.http import HttpResponse
from django.shortcuts import render, redirect
from trueskill import Rating, rate

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

    players = []
    for player in Player.objects.all():
        players.append([player.id, player.name])

    all_players = [p.to_dict_with_skill(activity["id"]) for p in Player.objects.all()]
    all_players.sort(key=lambda p: p["skill"] , reverse=True)
    top_players = all_players[:5]
    context = {
        'activities': activities,
        'activity': activity,
        'players': all_players,
        'active_players': [p for p in top_players],
        'matches': [m.__dict__ for m in Result.objects.all()],
        'pending_matches': [m.to_dict_with_teams() for m in Result.objects.filter(validated=0)],
        'deletable_match_ids': [],
        'player_ids': players
    }
    return render(request, 'activity_summary.html', context)


def list_players(request, activity_url):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect('home')

    context = {
        'activities': activities,
        'activity': activity,
        'players': [p.__dict__ for p in Player.objects.all()],
        'active_players': [p.to_dict_with_skill(activity["id"]) for p in Player.objects.all()],
    }
    return render(request, 'list_players.html', context)


def player_info(request, activity_url, player_id):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return redirect('home')

    player = Player.objects.filter(id=player_id)[0]
    context = {
        'activities': activities,
        'activity': activity,
        'player_info': player.to_dict_with_skill(activity_url),
        'player_id': player_id,
    }
    return render(request, 'player.html', context)


def player_history(request, activity_url, player_id):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return HttpResponse(json.dumps({'skill_history': []}))

    history = SkillHistory.objects.filter(player_id=player_id, activity_id=activity_url)
    return HttpResponse(json.dumps({'skill_history': [h.calc_skill() for h in history]}))


def list_matches(request, activity_url):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return HttpResponse(json.dumps({'skill_history': []}))

    players = []
    for player in Player.objects.all():
        players.append([player.id, player.name])
    context = {
        'activities': activities,
        'activity': activity,
        'player_ids': players,
        'matches': [m.to_dict_with_teams() for m in Result.objects.all()[:50]],
        'pending_matches': [m.to_dict_with_teams() for m in Result.objects.filter(validated=0)],
    }
    return render(request, 'list_matches.html', context)


def update(request, activity_url):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    activity = next((a for a in activities if a["url"] == activity_url), None)
    if activity is None:
        return HttpResponse("Activity not found.")

    start = time.time()
    batch_update_player_skills(activity["id"])
    end = time.time()
    return HttpResponse("Update completed in %.2fs" % (end - start))


def get_players(request, activity_url):
    return HttpResponse("")


def validate_match(request, activity_url):
    return HttpResponse("")


def submit_match(request, activity_url):
    return HttpResponse("")


def about(request):
    activities = [a.to_dict_with_url() for a in Activity.objects.all()]
    context = {
        'activities': activities
    }
    return render(request, 'about.html', context)


def batch_update_player_skills(activity_id):
    activity = Activity.objects.filter(id=activity_id)

    # Clear skill history that will be reconstructed
    SkillHistory.objects.filter(activity_id=activity_id).delete()

    # Setup initial ratings for each player
    start_mu = 25
    start_sigma = 25 / 3.0
    ratings = {p.id: Rating(start_mu, start_sigma) for p in Player.objects.all()}

    # Process each match to calculate rating progress and determine final rankings
    for result in Result.objects.filter(activity=activity):
        teams = AdhocTeam.objects.filter(result=result)

        team_ratings = []
        for team in teams:
            team_members = TeamMember.objects.filter(team=team)
            team_ratings.append([ratings[member.player.id] for member in team_members])

        if teams[0].ranking == 1 and teams[1].ranking == 2:
            team_ratings = rate([team_ratings[0], team_ratings[1]], ranks=[1, 2])
        elif teams[0].ranking == 2 and teams[1].ranking == 1:
            team_ratings = rate([team_ratings[0], team_ratings[1]], ranks=[2, 1])
        else:
            assert False, "Could not process match %s: unknown winning team" % (result.id)

        # Update current ratings and save them to SkillHistory
        for idx_team, team in enumerate(teams):
            team_members = TeamMember.objects.filter(team=team)
            for idx_member, member in enumerate(team_members):
                ratings[member.player.id] = team_ratings[idx_team][idx_member]
                history = SkillHistory(activity_id=activity_id, result=result,
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
