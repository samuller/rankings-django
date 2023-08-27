"""Tests for this app."""
import json
import time
from typing import List

from .models import (
    Activity,
    Player,
    GameSession,
    Game,
    AdhocTeam,
    TeamMember,
    Result,
    SkillHistory,
)

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

# from .views import submit_match


def change_per_value(arr: List) -> List:
    """Calculate the change in neighbouring values of the array."""
    return [next - prev for prev, next in zip(arr[0:-2], arr[1:-1])]


class BasicDataTestCase(TestCase):
    """Basic tests."""

    activity_url = "tennis"
    player_names = ["Zeus", "Hades"]
    matches = [
        [0, 1],
    ] * 10 + [
        [1, 0],
    ] * 5

    def setUp(self) -> None:
        """Test set-up."""
        self.client = Client()
        activity = Activity.objects.create(
            id=self.activity_url, url=self.activity_url, name=self.activity_url
        )
        players = []
        for name in self.player_names:
            player = Player.objects.create(name=name, email=f"{name.lower()}")
            players.append(player)

        self.create_matches(activity, players, self.matches)

    def create_matches(self, activity, players, matches):
        """Help to create matches for tests."""
        for match in matches:
            submission_time = time.time()
            submittor = "test.setup"
            session = GameSession.objects.create(
                activity=activity,
                validated=None,
                datetime=submission_time,
                submittor=submittor,
            )
            game_idx = 0
            game = Game.objects.create(
                session=session,
                position=game_idx,
                datetime=submission_time,
                submittor=submittor,
            )

            team = AdhocTeam.objects.create(session=session)
            TeamMember.objects.create(
                team=team, player=players[match[0]], validated=None
            )
            Result.objects.create(game=game, team=team, ranking=1)

            team = AdhocTeam.objects.create(session=session)
            TeamMember.objects.create(
                team=team, player=players[match[1]], validated=None
            )
            Result.objects.create(game=game, team=team, ranking=2)

    def test_main_page_activity(self) -> None:
        """Test main page lists activity."""
        act = self.activity_url
        assert Activity.objects.filter(url=act).count() == 1
        response = self.client.get("/")
        assert response.status_code == 200
        assert f'<li><a href="/{act}">{act}</a></li>' in str(response.content)

    def test_gen_activity_summary_page(self) -> None:
        """Test generation of activity summary page."""
        act = self.activity_url
        response = self.client.get(f"/{act}", follow=True)
        assert response.status_code == 200, response.status_code
        content = str(response.content)
        assert '<h3 class="title">Top players</h3>' in content
        assert '<h3 class="title">Pending match results</h3>' in content

    def test_gen_player_page(self) -> None:
        """Test generation of player page."""
        act = self.activity_url
        response = self.client.get(f"/{act}/player/1", follow=True)
        assert response.status_code == 200, response.status_code
        content = str(response.content)
        for expected_word in [
            "Skill progression",
            "Current skill estimate",
            "Skill level",
            "Matches played",
        ]:
            assert expected_word in content, expected_word

    def test_gen_about_page(self) -> None:
        """Test generation of about page."""
        response = self.client.get("/about", follow=True)
        assert response.status_code == 200, response.status_code
        content = str(response.content)
        for expected_word in [
            "Trueskill",
            "Website",
            "Bayesian probability",
            "Zurb Foundation",
        ]:
            assert expected_word in content, expected_word

    def test_activity_page_matches(self) -> None:
        """Test activity page lists matches."""
        act = self.activity_url
        response = self.client.get(f"/{act}/matches")
        assert response.status_code == 200, response.status_code
        content = str(response.content)
        assert '<h3 class="title">Match history</h3>' in content
        # TODO: check matches

    def test_activity_page_players(self) -> None:
        """Test activity page lists players."""
        act = self.activity_url
        response = self.client.get(f"/{act}/players/name")
        assert response.status_code == 200, response.status_code
        all_players = [
            # Skills will still be empty/zero as we haven't calculated them yet.
            p.to_dict_with_skill(act)
            for p in Player.objects.filter(active=True)
        ]
        all_names = [p["name"] for p in all_players]
        for idx, name in enumerate(self.player_names):
            # Players aren't shown until they've played a few games.
            assert f'<a href="/{act}/player/{idx}">{name}</a>' not in str(
                response.content
            )
            assert name in all_names

    def check_expected_skill_changes(self):
        """
        Check the expected changes in calculated skill.

        Separate function to allow re-use and cross-checking between incremental and full approach.
        """
        # Check that skill changes as expected according to win/losses.
        history = SkillHistory.objects.all()
        skill_zeus = [h.calc_skill() for h in history if h.player.name == "Zeus"]
        skill_hades = [h.calc_skill() for h in history if h.player.name == "Hades"]
        assert all(diff > 0 for diff in change_per_value(skill_zeus[0:10]))
        assert all(diff < 0 for diff in change_per_value(skill_zeus[10:]))
        # Only increases due to smaller sigma.
        assert all(
            diff < 0.5 for diff in change_per_value(skill_hades[0:10])
        ), skill_hades
        assert all(diff > 0 for diff in change_per_value(skill_hades[10:]))
        # Check that mu changes as expected according to win/losses.
        mu_zeus = [h.mu for h in history if h.player.name == "Zeus"]
        mu_hades = [h.mu for h in history if h.player.name == "Hades"]
        assert all(diff > 0 for diff in change_per_value(mu_zeus[0:10]))
        assert all(diff < 0 for diff in change_per_value(mu_zeus[10:]))
        assert all(diff < 0 for diff in change_per_value(mu_hades[0:10]))
        assert all(diff > 0 for diff in change_per_value(mu_hades[10:]))
        # Check that sigma always decreases.
        sigma_zeus = [h.sigma for h in history if h.player.name == "Zeus"]
        sigma_hades = [h.sigma for h in history if h.player.name == "Hades"]
        assert all(diff < 0 for diff in change_per_value(sigma_zeus))
        assert all(diff < 0 for diff in change_per_value(sigma_hades))

    def test_calculated_rankings(self) -> None:
        """Tets calculated rankings."""
        # Validate all matches as following skill calculation runs only on validated matches.
        GameSession.objects.all().update(validated=True)
        TeamMember.objects.all().update(validated=True)

        act = self.activity_url
        # First request will fail as superuser is required (follow needed for redirect).
        response = self.client.get(f"/{act}/update", follow=True)
        assert response.status_code == 404, response.status_code

        User.objects.create_superuser("adm", "admin@example.com", "passw")
        self.client.login(username="adm", password="passw")
        response = self.client.get(f"/{act}/update")
        self.client.logout()
        assert response.status_code == 200, response.status_code

        self.check_expected_skill_changes()

    def test_admin_incremental_skill_update_at_once(self) -> None:
        """Test incremental skill updates (via the admin tool) done for all matches at once."""
        User.objects.create_superuser("adm2", "admin2@example.com", "passw2")
        self.client.login(username="adm2", password="passw2")

        # TODO: test order independence of incremental function (.order_by("id"))
        session_ids = GameSession.objects.values_list("id", flat=True)
        data = {
            "action": "validate_matches_and_update_skill",
            "_selected_action": session_ids,
        }
        change_url = reverse("admin:previous_gamesession_changelist")
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()

        messages = [str(msg) for msg in list(response.context["messages"])]
        assert len(messages) == 1, messages
        assert messages[0].startswith("GameSessions validated in 0."), messages
        self.assertEqual(response.status_code, 200)

        self.check_expected_skill_changes()

    def test_admin_incremental_skill_update_in_steps(self) -> None:
        """Test incremental skil updates (via the admin tool) done for each match separately."""
        User.objects.create_superuser("adm2", "admin2@example.com", "passw2")
        self.client.login(username="adm2", password="passw2")

        # TODO: test order independence of incremental function (.order_by("id"))
        session_ids = GameSession.objects.values_list("id", flat=True)
        for session_id in session_ids:
            data = {
                "action": "validate_matches_and_update_skill",
                "_selected_action": [session_id],
            }
            change_url = reverse("admin:previous_gamesession_changelist")
            response = self.client.post(change_url, data, follow=True)

            messages = [str(msg) for msg in list(response.context["messages"])]
            assert len(messages) == 1, messages
            assert messages[0].startswith("GameSessions validated in 0."), messages
            self.assertEqual(response.status_code, 200)
        self.client.logout()
        assert GameSession.objects.filter(validated__isnull=True).count() == 0
        self.check_expected_skill_changes()

    def test_submission(self) -> None:
        """Test submitting match results."""
        activity = Activity.objects.get(url=self.activity_url)
        assert activity is not None
        before_count = GameSession.objects.filter(activity=activity).count()

        # submit_match()
        response = self.client.post(
            f"/{self.activity_url}/api/add_matches",
            json.dumps({"teams": [[[1], [2]], [[1], [2]]], "wins": [1, 2]}),
            content_type="application/json",
        )
        assert response.status_code == 200

        after_count = GameSession.objects.filter(activity=activity).count()
        assert (after_count - before_count) == 2
