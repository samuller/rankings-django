from django.http import HttpResponse
from django.shortcuts import render, redirect

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

    context = {
        'activities': activities,
        'activity': activity,
        'players': [p.__dict__ for p in Player.objects.all()],
        'active_players': [p.to_dict_with_skill(activity["id"]) for p in Player.objects.all()],
        'matches': [],
        'pending_matches': [],
        'deletable_match_ids': [],
    }
    return render(request, 'activity_summary.html', context)


def list_players(request, activity_url):
    context = {}
    return render(request, 'list_players.html', context)


def player_info(request, activity_url, player_id):
    context = {}
    return render(request, 'player.html', context)


def player_history(request, activity_url, player_id):
    return HttpResponse("")


def list_matches(request, activity_url):
    context = {}
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
    context = {}
    return render(request, 'about.html', context)

