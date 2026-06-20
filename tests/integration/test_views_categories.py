import pytest
from django.urls import reverse

from auctions.models import Comment
from tests.conftest import ListingFactory


@pytest.mark.django_db
class TestCategoriesAndCommentsViews:
    def test_categories_page_get(self, client):
        response = client.get(reverse("categories"))
        assert response.status_code == 200

    def test_categories_with_filter(self, client, user):
        ListingFactory(user=user, category="Electronics", title="Phone A")
        ListingFactory(user=user, category="Books", title="Novel B")
        response = client.get(reverse("categories") + "?category=Electronics")
        assert response.status_code == 200
        assert b"Phone A" in response.content
        assert b"Novel B" not in response.content

    def test_categories_no_results(self, client):
        response = client.get(reverse("categories") + "?category=Nonexistent")
        assert response.status_code == 200

    def test_categories_shows_db_categories(self, client, user):
        ListingFactory(user=user, category="Furniture", title="Chair X")
        response = client.get(reverse("categories"))
        assert response.status_code == 200
        assert b"Furniture" in response.content

    def test_comment_requires_login(self, client, listing):
        response = client.post(
            reverse("comment", args=[listing.id]),
            {"text": "Nice item!"},
        )
        assert response.status_code == 302
        assert "/login" in response.url

    def test_comment_post_creates_comment(self, client, user, listing):
        client.force_login(user)
        response = client.post(
            reverse("comment", args=[listing.id]),
            {"text": "This looks amazing!"},
        )
        assert response.status_code == 302
        assert Comment.objects.filter(
            listing=listing, user=user, text="This looks amazing!"
        ).exists()

    def test_comment_redirects_to_listing(self, client, user, listing):
        client.force_login(user)
        response = client.post(
            reverse("comment", args=[listing.id]),
            {"text": "Great auction!"},
        )
        assert response.status_code == 302
        assert str(listing.id) in response.url
