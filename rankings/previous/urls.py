from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main_page, name='home'),
    url(r'^about$', views.about, name='about'),
    url(r'^api/fix_player$', views.replace_player_in_submissions, name='fix_player'),
    url(r'^api/validate_all$', views.validate_all_matches),
    url(r'^select_player_to_fix/(?P<result_ids_str>.*)$', views.select_player_to_replace_in_submissions, name='select_fix_player'),
    url(r'^(?P<activity_url>.+)/$', views.activity_summary, name='activity_summary'),
    url(r'^(?P<activity_url>.+)/players$', views.list_players, name='list_players'),
    url(r'^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)$', views.player_info, name='player_info'),
    url(r'^(?P<activity_url>.+)/player/(?P<player_id>[0-9]+)/history$', views.player_history),
    url(r'^(?P<activity_url>.+)/matches$', views.list_matches, name='list_matches'),
    url(r'^(?P<activity_url>.+)/update$', views.update, name='update_rankings'),
    url(r'^(?P<activity_url>.+)/api/get_players$', views.get_players),
    url(r'^(?P<activity_url>.+)/api/add_matches$', views.submit_match),
    ]
