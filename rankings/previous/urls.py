"""Django URL patterns to redirect URL paths to specific views."""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.main_page, name="home"),
    url(r"^about$", views.about, name="about"),
    url(r"^api/id$", views.show_id),
    url(r"^api/fix_player$", views.replace_player_in_submissions, name="fix_player"),
    url(r"^api/validate_all$", views.validate_all_matches),
    url(
        r"^select_player_to_fix/(?P<session_ids_str>.*)$",
        views.select_player_to_replace_in_submissions,
        name="select_fix_player",
    ),
    url(r"^(?P<activity_url>[^/]+)/$", views.activity_summary, name="activity_summary"),
    url(
        r"^(?P<activity_url>.+)/players/(?P<sort_by>.*)$",
        views.list_players,
        name="list_players",
    ),
    url(
        r"^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)$",
        views.player_info,
        name="player_info",
    ),
    url(
        r"^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)/history$",
        views.player_history,
    ),
    url(r"^(?P<activity_url>.+)/matches$", views.list_matches, name="list_matches"),
    url(
        r"^(?P<activity_url>.+)/matches/(?P<page>[0-9]+)$",
        views.list_matches,
        name="list_matches",
    ),
    url(r"^(?P<activity_url>.+)/match/$", views.list_matches, name="list_match"),
    url(
        r"^(?P<activity_url>.+)/match/(?P<match_id>[0-9]+)$",
        views.list_matches,
        name="list_match",
    ),
    url(r"^(?P<activity_url>.+)/update$", views.update, name="update_rankings"),
    url(
        r"^(?P<activity_url>.+)/update/(?P<year>[0-9]+)$",
        views.update,
        name="update_rankings",
    ),
    url(r"^(?P<activity_url>.+)/api/get_players$", views.get_players),
    url(r"^(?P<activity_url>.+)/api/add_matches$", views.submit_match),
    url(r"^(?P<activity_url>.+)/api/undo_submission$", views.undo_submit),
]
