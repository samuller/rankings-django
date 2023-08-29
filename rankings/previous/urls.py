"""Django URL patterns to redirect URL paths to specific views."""
from django.urls import re_path, path, include
from rest_framework import routers

from . import views, api

router = routers.DefaultRouter()
router.register("activities", api.ActivityViewSet, basename="activities")

urlpatterns = [
    re_path(r"^$", views.main_page, name="home"),
    re_path(r"^about$", views.about, name="about"),
    re_path(r"^api/id$", api.show_source_id),
    re_path(r"^api/fix_player$", api.replace_player_in_submissions, name="fix_player"),
    re_path(r"^api/validate_all$", api.validate_all_matches),
    re_path(
        r"^select_player_to_fix/(?P<session_ids_str>.*)$",
        views.select_player_to_replace_in_submissions,
        name="select_fix_player",
    ),
    re_path(
        r"^(?P<activity_url>[^/]+)/$", views.activity_summary, name="activity_summary"
    ),
    re_path(
        r"^(?P<activity_url>.+)/players/(?P<sort_by>.*)$",
        views.list_players,
        name="list_players",
    ),
    re_path(
        r"^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)$",
        views.player_info,
        name="player_info",
    ),
    re_path(
        r"^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)/history$",
        views.player_history,
    ),
    re_path(r"^(?P<activity_url>.+)/matches$", views.list_matches, name="list_matches"),
    re_path(
        r"^(?P<activity_url>.+)/matches/(?P<page>[0-9]+)$",
        views.list_matches,
        name="list_matches",
    ),
    re_path(r"^(?P<activity_url>.+)/match/$", views.list_matches, name="list_match"),
    re_path(
        r"^(?P<activity_url>.+)/match/(?P<match_id>[0-9]+)$",
        views.list_matches,
        name="list_match",
    ),
    re_path(r"^(?P<activity_url>.+)/update$", views.update, name="update_rankings"),
    re_path(
        r"^(?P<activity_url>.+)/update/(?P<year>[0-9]+)$",
        views.update,
        name="update_rankings",
    ),
    re_path(r"^(?P<activity_url>.+)/api/get_players$", api.get_players),
    re_path(r"^(?P<activity_url>.+)/api/add_matches$", api.submit_match),
    re_path(r"^(?P<activity_url>.+)/api/undo_submission$", api.undo_submit),
    path("api/", include(router.urls)),
]
