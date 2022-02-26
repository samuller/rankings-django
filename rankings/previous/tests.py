"""Tests for this app."""
import json
from django.test import TestCase, Client
from .models import Activity, Player, GameSession

# from .views import submit_match


class BasicDataTestCase(TestCase):
    """Basic tests."""

    activity_url = "tennis"

    def setUp(self):
        """Test set-up."""
        self.client = Client()
        Activity.objects.create(url=self.activity_url, name=self.activity_url)
        Player.objects.create(name="Zeus", email="zeus")
        Player.objects.create(name="Hades", email="hades")

    def test_main_page(self):
        """Test main page lists activity."""
        assert Activity.objects.filter(url=self.activity_url).count() == 1
        response = self.client.get("/")
        assert response.status_code == 200
        act = self.activity_url
        assert f'<li><a href="/{act}">{act}</a></li>' in str(response.content)

    def test_submission(self):
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
