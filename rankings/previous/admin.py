"""Django Admin tool configuration."""

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
    """Admin view for Activities."""

    list_display = ("__str__",)
    actions = [
        "recalc_skill_rankings",
        "recalc_skill_rankings_for_current_calendar_year",
    ]

    def recalc_skill_rankings(self, request, queryset):
        """Define action to completely clear and recalculate the skill rankings."""
        if queryset.count() > 1:
            self.message_user(
                request,
                "Can not update more than one activity at once.",
                level=messages.constants.WARNING,
            )
            return

        return HttpResponseRedirect(reverse("update_rankings", kwargs={"activity_url": queryset.first().id}))

    def recalc_skill_rankings_for_current_calendar_year(self, request, queryset):
        """Define action to recalculate the skill rankings, but only consider games for the current year."""
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
    """Admin view for Players."""

    list_display = ("name", "email", "active")


class RankingAdmin(admin.ModelAdmin):
    """Admin view for Rankings."""

    list_display = ("__str__",)


class GameSessionAdmin(admin.ModelAdmin):
    """Admin view for GameSessions."""

    list_display = ("__str__", "result_summary", "validation")
    list_filter = ("validated", "activity")
    # date_hierarchy = 'datetime'
    actions = [
        "validate_matches_and_update_skill",
        "invalidate_matches",
        "fix_incorrect_player",
    ]

    def result_summary(self, obj):
        """Define display column to show a short summary of the GameSession."""
        return obj.summary_str()

    result_summary.short_description = "Summary"  # type: ignore

    def validation(self, obj):
        """Define display column to indicate showing validation as a boolean."""
        return obj.validated

    validation.boolean = True  # type: ignore

    def validate_matches_and_update_skill(self, request, queryset):
        """Define action to declare a submission to be valid and update the skill of all players involved."""
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
            # Null = unvalidated, True = validated, False = invalidated
            GameSession.objects.filter(activity=activity, validated__isnull=True).order_by("datetime").first()
        )
        if earliest_match != first_unvalidated:
            messages.error(
                request,
                "Can't skip unvalidated sessions - validation has to occur in order"
                + f" (see: {first_unvalidated.id if first_unvalidated is not None else None})",
            )
            return

        start = time.time()
        # Update player skills
        incremental_update_player_skills(queryset)
        # Validate sessions
        queryset.update(validated=True)
        end = time.time()
        self.message_user(request, f"GameSessions validated in {end - start:.2f}s")

    def invalidate_matches(self, request, queryset):
        """Define action to set a submission as invalid."""
        queryset.update(validated=False)
        self.message_user(request, "GameSessions invalidated")

    def fix_incorrect_player(self, request, queryset):
        """Define action to fix an incorrectly selected player in a GameSession submission."""
        result_ids = ",".join([str(val[0]) for val in queryset.values_list("id")])
        return HttpResponseRedirect(reverse("select_fix_player", kwargs={"session_ids_str": result_ids}))


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
