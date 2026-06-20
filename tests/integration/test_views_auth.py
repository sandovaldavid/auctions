import pytest
from django.urls import reverse

from tests.conftest import UserFactory


@pytest.mark.django_db
class TestAuthViews:
    def test_index_returns_200(self, client):
        response = client.get(reverse("index"))
        assert response.status_code == 200

    def test_login_page_get(self, client):
        response = client.get(reverse("login"))
        assert response.status_code == 200

    def test_login_success(self, client, user):
        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "testpassword123"},
        )
        assert response.status_code == 302
        assert response.url == reverse("index")

    def test_login_wrong_password(self, client, user):
        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "wrongpassword"},
        )
        assert response.status_code == 200
        assert b"Invalid" in response.content

    def test_logout_redirects(self, client, user):
        client.force_login(user)
        response = client.get(reverse("logout"))
        assert response.status_code == 302
        assert response.url == reverse("index")

    def test_register_get(self, client):
        response = client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_success(self, client, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        response = client.post(
            reverse("register"),
            {
                "username": "brandnewuser",
                "email": "brandnew@example.com",
                "password": "securepass99",
                "confirmation": "securepass99",
            },
        )
        assert response.status_code == 302
        assert User.objects.filter(username="brandnewuser").exists()

    def test_register_password_mismatch(self, client, db):
        response = client.post(
            reverse("register"),
            {
                "username": "someuser",
                "email": "some@example.com",
                "password": "pass1",
                "confirmation": "pass2",
            },
        )
        assert response.status_code == 200
        assert b"match" in response.content

    def test_register_existing_username(self, client, user):
        response = client.post(
            reverse("register"),
            {
                "username": user.username,
                "email": "other@example.com",
                "password": "testpassword123",
                "confirmation": "testpassword123",
            },
        )
        assert response.status_code == 200
        assert b"already taken" in response.content

    def test_new_auction_requires_login(self, client):
        response = client.get(reverse("new_auction"))
        assert response.status_code == 302
        assert "/login" in response.url
