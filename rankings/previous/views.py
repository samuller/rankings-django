from django.http import HttpResponse
from django.shortcuts import render, redirect
import json

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
    context = {
        'activities': activities,
        'activity': activity,
        'players': [p.__dict__ for p in Player.objects.all()],
        'active_players': [p.to_dict_with_skill(activity["id"]) for p in Player.objects.all()],
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
    return HttpResponse("")


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

