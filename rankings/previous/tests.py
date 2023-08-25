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
    matches = [[0, 1],] * 10 + [
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
                validated=True,
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
                team=team, player=players[match[0]], validated=True
            )
            Result.objects.create(game=game, team=team, ranking=1)

            team = AdhocTeam.objects.create(session=session)
            TeamMember.objects.create(
                team=team, player=players[match[1]], validated=True
            )
            Result.objects.create(game=game, team=team, ranking=2)

    def test_main_page_activity(self) -> None:
        """Test main page lists activity."""
        act = self.activity_url
        assert Activity.objects.filter(url=act).count() == 1
        response = self.client.get("/")
        assert response.status_code == 200
        assert f'<li><a href="/{act}">{act}</a></li>' in str(response.content)

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

    def test_calculated_rankings(self) -> None:
        """Tets calculated rankings."""
        act = self.activity_url
        # First request will fail as superuser is required (we end URL with a backslash due to Django's
        # APPEND_SLASH which any failures to become redirects and then the actual error status code
        # is only seen after the slash has been appended).
        response = self.client.get(f"/{act}/update/")
        assert response.status_code == 404, response.status_code

        User.objects.create_superuser("adm", "admin@example.com", "passw")
        self.client.login(username="adm", password="passw")
        response = self.client.get(f"/{act}/update")
        assert response.status_code == 200, response.status_code

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
