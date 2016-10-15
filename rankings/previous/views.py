from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.


def main_page(request):
    context = {}
    return render(request, 'main_page.html', context)


def validate_all_matches(request):
    return HttpResponse("")


def activity_summary(request, activity_url):
    return HttpResponse("")


def list_players(request, activity_url):
    return HttpResponse("")


def player_info(request, activity_url, player_id):
    return HttpResponse("")


def player_history(request, activity_url, player_id):
    return HttpResponse("")


def list_matches(request, activity_url):
    return HttpResponse("")


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

