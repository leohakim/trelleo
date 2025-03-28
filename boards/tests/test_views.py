import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from boards.models import Attachment, Board, Card, Comment, Label, List


@pytest.fixture
def client():
    """Create a test client"""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated client"""
    client.login(username="testuser", password="password123")
    return client


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestHomeView:
    """Tests for the home view"""

    def test_home_view_authenticated(self, authenticated_client):
        """Test that authenticated users are redirected to the board list"""
        response = authenticated_client.get(reverse("boards:home"))
        assert response.status_code == 302
        assert response.url == reverse("boards:board_list")

    def test_home_view_unauthenticated(self, client):
        """Test that unauthenticated users see the home page"""
        response = client.get(reverse("boards:home"))
        assert response.status_code == 200
        assert b"Welcome to Trelleo" in response.content


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestAuthViews:
    """Tests for authentication views"""

    def test_register_view_get(self, client):
        """Test that the register view returns a form"""
        response = client.get(reverse("boards:register"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_register_view_post_valid(self, client):
        """Test that a user can register with valid data"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        response = client.post(reverse("boards:register"), data)
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_register_view_post_invalid(self, client):
        """Test that registration fails with invalid data"""
        data = {
            "username": "newuser",
            "email": "invalid-email",
            "password1": "password123",
            "password2": "different_password",
        }
        response = client.post(reverse("boards:register"), data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_profile_view_unauthenticated(self, client):
        """Test that unauthenticated users are redirected to login"""
        response = client.get(reverse("boards:profile"))
        assert response.status_code == 302
        assert "login" in response.url


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestBoardViews:
    """Tests for board views"""

    def test_board_create_view_post_valid(self, authenticated_client, user):
        """Test that a board can be created with valid data"""
        data = {
            "title": "New Board",
            "description": "This is a new board",
            "background_color": "#0079BF",
        }
        response = authenticated_client.post(reverse("boards:board_create"), data)
        assert response.status_code == 302
        assert Board.objects.filter(title="New Board").exists()

    def test_board_edit_view_post_valid(self, authenticated_client, board):
        """Test that a board can be edited with valid data"""
        data = {
            "title": "Updated Board",
            "description": "This is an updated board",
            "background_color": "#0079BF",
        }
        response = authenticated_client.post(
            reverse("boards:board_edit", kwargs={"slug": board.slug}), data
        )
        assert response.status_code == 302
        board.refresh_from_db()
        assert board.title == "Updated Board"

    def test_board_delete_view(self, authenticated_client, board):
        """Test that a board can be deleted"""
        response = authenticated_client.post(
            reverse("boards:board_delete", kwargs={"slug": board.slug})
        )
        assert response.status_code == 302
        assert not Board.objects.filter(id=board.id).exists()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestListViews:
    """Tests for list views"""

    def test_list_create_view_post(self, authenticated_client, board):
        """Test that a list can be created"""
        data = {
            "title": "New List",
        }
        response = authenticated_client.post(
            reverse("boards:list_create", kwargs={"slug": board.slug}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert List.objects.filter(title="New List").exists()

    def test_list_edit_view_post(self, authenticated_client, list_obj):
        """Test that a list can be edited"""
        data = {
            "title": "Updated List",
        }
        response = authenticated_client.post(
            reverse("boards:list_edit", kwargs={"pk": list_obj.pk}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        list_obj.refresh_from_db()
        assert list_obj.title == "Updated List"

    def test_list_delete_view(self, authenticated_client, list_obj):
        """Test that a list can be deleted"""
        response = authenticated_client.post(
            reverse("boards:list_delete", kwargs={"pk": list_obj.pk})
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert not List.objects.filter(id=list_obj.id).exists()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestCardViews:
    """Tests for card views"""

    def test_card_create_view_post(self, authenticated_client, list_obj):
        """Test that a card can be created"""
        data = {
            "title": "New Card",
            "description": "This is a new card",
        }
        response = authenticated_client.post(
            reverse("boards:card_create", kwargs={"list_id": list_obj.pk}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert Card.objects.filter(title="New Card").exists()

    def test_card_edit_view_post(self, authenticated_client, card):
        """Test that a card can be edited"""
        data = {
            "title": "Updated Card",
            "description": "This is an updated card",
            "list": card.list.id,
        }
        response = authenticated_client.post(
            reverse("boards:card_edit", kwargs={"pk": card.pk}), data
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        card.refresh_from_db()
        assert card.title == "Updated Card"

    def test_card_delete_view(self, authenticated_client, card):
        """Test that a card can be deleted"""
        response = authenticated_client.post(
            reverse("boards:card_delete", kwargs={"pk": card.pk})
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert not Card.objects.filter(id=card.id).exists()

    def test_card_toggle_complete_view(self, authenticated_client, card):
        """Test that a card's completion status can be toggled"""
        # Get the initial completion status
        initial_status = card.is_completed

        response = authenticated_client.post(
            reverse("boards:card_toggle_complete", kwargs={"pk": card.pk})
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        card.refresh_from_db()
        assert card.is_completed != initial_status


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestLabelViews:
    """Tests for label views"""

    def test_label_create_view_post(self, authenticated_client, board):
        """Test that a label can be created"""
        data = {
            "name": "New Label",
            "color": "#FF0000",
        }
        response = authenticated_client.post(
            reverse("boards:label_create", kwargs={"board_slug": board.slug}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert Label.objects.filter(name="New Label").exists()

    def test_label_edit_view_post(self, authenticated_client, label):
        """Test that a label can be edited"""
        data = {
            "name": "Updated Label",
            "color": "#00FF00",
        }
        response = authenticated_client.post(
            reverse("boards:label_edit", kwargs={"pk": label.pk}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        label.refresh_from_db()
        assert label.name == "Updated Label"

    def test_label_delete_view(self, authenticated_client, label):
        """Test that a label can be deleted"""
        response = authenticated_client.post(
            reverse("boards:label_delete", kwargs={"pk": label.pk})
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        assert not Label.objects.filter(id=label.id).exists()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestCommentViews:
    """Tests for comment views"""

    def test_comment_create_view_post(self, authenticated_client, card, user):
        """Test that a comment can be created"""
        data = {
            "text": "This is a new comment",
        }
        response = authenticated_client.post(
            reverse("boards:comment_create", kwargs={"card_id": card.pk}), data
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        assert Comment.objects.filter(text="This is a new comment").exists()

    def test_comment_edit_view_post(self, authenticated_client, comment):
        """Test that a comment can be edited"""
        data = {
            "text": "This is an updated comment",
        }
        response = authenticated_client.post(
            reverse("boards:comment_edit", kwargs={"pk": comment.pk}), data
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        comment.refresh_from_db()
        assert comment.text == "This is an updated comment"

    def test_comment_delete_view(self, authenticated_client, comment):
        """Test that a comment can be deleted"""
        response = authenticated_client.post(
            reverse("boards:comment_delete", kwargs={"pk": comment.pk})
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestAttachmentViews:
    """Tests for attachment views"""

    def test_attachment_delete_view(self, authenticated_client, attachment):
        """Test that an attachment can be deleted"""
        response = authenticated_client.post(
            reverse("boards:attachment_delete", kwargs={"pk": attachment.pk})
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        assert not Attachment.objects.filter(id=attachment.id).exists()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestBoardMemberViews:
    """Tests for board member views"""

    def test_board_add_member_view(self, authenticated_client, board, db):
        """Test that a member can be added to a board"""
        # Create a new user to add as a member
        member = User.objects.create_user(
            username="member", email="member@example.com", password="password123"
        )

        data = {
            "username": "member",
        }
        response = authenticated_client.post(
            reverse("boards:board_add_member", kwargs={"slug": board.slug}), data
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        board.refresh_from_db()
        assert member in board.members.all()

    def test_board_remove_member_view(self, authenticated_client, board, db):
        """Test that a member can be removed from a board"""
        # Create a new user, then add to board
        member = User.objects.create_user(
            username="member", email="member@example.com", password="password123"
        )
        board.members.add(member)

        response = authenticated_client.post(
            reverse(
                "boards:board_remove_member",
                kwargs={"slug": board.slug, "user_id": member.id},
            )
        )
        # Expect a redirect to the board detail page
        assert response.status_code == 302
        board.refresh_from_db()
        assert member not in board.members.all()


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestCardMemberViews:
    """Tests for card member views"""

    def test_card_add_member_view(self, authenticated_client, card, board, db):
        """Test that a member can be added to a card"""
        # Create a new user, add to board, then add to card
        member = User.objects.create_user(
            username="member", email="member@example.com", password="password123"
        )
        board.members.add(member)

        data = {
            "user_id": member.id,
        }
        response = authenticated_client.post(
            reverse("boards:card_add_member", kwargs={"pk": card.pk}), data
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        card.refresh_from_db()
        assert member in card.members.all()

    def test_card_remove_member_view(self, authenticated_client, card, board, db):
        """Test that a member can be removed from a card"""
        # Create a new user, add to board, then add to card
        member = User.objects.create_user(
            username="member", email="member@example.com", password="password123"
        )
        board.members.add(member)
        card.members.add(member)

        response = authenticated_client.post(
            reverse(
                "boards:card_remove_member",
                kwargs={"pk": card.pk, "user_id": member.id},
            )
        )
        # Expect a redirect to the card detail page
        assert response.status_code == 302
        card.refresh_from_db()
        assert member not in card.members.all()
