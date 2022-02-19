import time
import datetime

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .views import incremental_update_player_skills, get_common_activity
from .models import (
    Activity,
    AdhocTeam,
    Player,
    Ranking,
    Game,
    GameSession,
    Result,
    SkillHistory,
    SkillType,
    TeamMember,
)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    actions = [
        "recalc_skill_rankings",
        "recalc_skill_rankings_for_current_calendar_year",
    ]

    def recalc_skill_rankings(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Can not update more than one activity at once.",
                level=messages.constants.WARNING,
            )
            return

        return HttpResponseRedirect(
            reverse("update_rankings", kwargs={"activity_url": queryset.first().id})
        )

    def recalc_skill_rankings_for_current_calendar_year(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Can not update more than one activity at once.",
                level=messages.constants.WARNING,
            )
            return

        return HttpResponseRedirect(
            reverse(
                "update_rankings",
                kwargs={
                    "activity_url": queryset.first().id,
                    "year": datetime.datetime.now().year,
                },
            )
        )


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "active")


class RankingAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "result_summary", "validation")
    list_filter = ("validated",)
    # date_hierarchy = 'datetime'
    actions = [
        "validate_matches_and_update_skill",
        "invalidate_matches",
        "fix_incorrect_player",
    ]

    def result_summary(self, obj):
        return obj.summary_str()

    result_summary.short_description = "Summary"

    def validation(self, obj):
        return obj.validated

    validation.boolean = True

    def validate_matches_and_update_skill(self, request, queryset):
        # Check all session are for the same activity
        activity = get_common_activity(queryset)
        if activity is None:
            messages.error(request, "All sessions have to be for the same activity")
            return
        # Check that sessions aren't double validated
        if queryset.filter(validated=True).count() != 0:
            messages.error(request, "Can't validate sessions again")
            return
        # Check that matches aren't skipped/out of order, else skill
        # update will be slightly affected
        earliest_match = queryset.order_by("datetime").first()
        first_unvalidated = (
            GameSession.objects.filter(activity=activity, validated__isnull=True)
            .order_by("datetime")
            .first()
        )
        if earliest_match != first_unvalidated:
            messages.error(
                request,
                "Can't skip unvalidated sessions - validation has to occur in order"
                + " (see: %s)" % (first_unvalidated.id,),
            )
            return

        start = time.time()
        # Validate sessions
        queryset.update(validated=True)
        # Update player skills
        incremental_update_player_skills(queryset)
        end = time.time()
        self.message_user(request, "GameSessions validated in %.2fs" % (end - start))

    def invalidate_matches(self, request, queryset):
        queryset.update(validated=False)
        self.message_user(request, "GameSessions invalidated")

    def fix_incorrect_player(self, request, queryset):
        result_ids = ",".join([str(val[0]) for val in queryset.values_list("id")])
        return HttpResponseRedirect(
            reverse("select_fix_player", kwargs={"session_ids_str": result_ids})
        )


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
