from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    actions = ['update_skill_rankings']
    
    def update_skill_rankings(self, request, queryset):
      if queryset.count() > 1:
        self.message_user(request, "Can not update more than one activity at once.",
          level=messages.constants.WARNING)
        return
      
      return HttpResponseRedirect(reverse('update_rankings',
        kwargs={'activity_url': queryset.first().id}))

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

class RankingAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'result_summary', 'validation')
    list_filter = ('validated',)
    # date_hierarchy = 'datetime'
    actions = ['validate_matches', 'invalidate_matches', 'fix_incorrect_player']

    def result_summary(self, obj):
      return obj.summary_str()
    result_summary.short_description = 'Summary'
    
    def validation(self, obj):
      return obj.validated
    validation.boolean = True
    
    def validate_matches(self, request, queryset):
      queryset.update(validated=True)
      self.message_user(request, "GameSessions validated")

    def invalidate_matches(self, request, queryset):
      queryset.update(validated=False)
      self.message_user(request, "GameSessions invalidated")

    def fix_incorrect_player(self, request, queryset):
      result_ids = ",".join([str(val[0]) for val in queryset.values_list('id')])
      return HttpResponseRedirect(reverse('select_fix_player',
        kwargs={'session_ids_str': result_ids}))


# Register your models here.
admin.site.register(Activity, ActivityAdmin)
admin.site.register(AdhocTeam)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(Game)
admin.site.register(Result)
admin.site.register(SkillHistory)
admin.site.register(SkillType)
admin.site.register(TeamMember)

