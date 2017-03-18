from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

class RankingAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

class ResultAdmin(admin.ModelAdmin):
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
      self.message_user(request, "Matches validated")

    def invalidate_matches(self, request, queryset):
      queryset.update(validated=False)
      self.message_user(request, "Matches invalidated")

    def fix_incorrect_player(self, request, queryset):
      result_ids = ",".join([str(val[0]) for val in queryset.values_list('id')])
      return HttpResponseRedirect(reverse('select_fix_player',
        kwargs={'result_ids_str': result_ids}))


# Register your models here.
admin.site.register(Activity)
admin.site.register(AdhocTeam)
#admin.site.register(Player, PlayerAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(ResultSet)
admin.site.register(ResultSetMember)
admin.site.register(SkillHistory)
admin.site.register(SkillType)
admin.site.register(TeamMember)

