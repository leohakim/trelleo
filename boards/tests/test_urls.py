import pytest
from django.urls import resolve, reverse

from boards import views


@pytest.mark.urls("trelleo.urls")
@pytest.mark.unit
class TestBoardsUrls:
    """Tests for the boards app URL patterns"""

    def test_home_url(self):
        """Test the home URL pattern"""
        url = reverse("boards:home")
        assert url == "/"
        assert resolve(url).func == views.home

    def test_board_list_url(self):
        """Test the board list URL pattern"""
        url = reverse("boards:board_list")
        assert url == "/boards/"
        assert resolve(url).func == views.board_list

    def test_board_create_url(self):
        """Test the board create URL pattern"""
        url = reverse("boards:board_create")
        assert url == "/boards/create/"
        assert resolve(url).func == views.board_create

    def test_board_detail_url(self):
        """Test the board detail URL pattern"""
        url = reverse("boards:board_detail", kwargs={"slug": "test-board"})
        assert url == "/boards/test-board/"
        assert resolve(url).func == views.board_detail

    def test_board_edit_url(self):
        """Test the board edit URL pattern"""
        url = reverse("boards:board_edit", kwargs={"slug": "test-board"})
        assert url == "/boards/test-board/edit/"
        assert resolve(url).func == views.board_edit

    def test_board_delete_url(self):
        """Test the board delete URL pattern"""
        url = reverse("boards:board_delete", kwargs={"slug": "test-board"})
        assert url == "/boards/test-board/delete/"
        assert resolve(url).func == views.board_delete

    def test_list_create_url(self):
        """Test the list create URL pattern"""
        url = reverse("boards:list_create", kwargs={"slug": "test-board"})
        assert url == "/boards/test-board/lists/create/"
        assert resolve(url).func == views.list_create

    def test_list_edit_url(self):
        """Test the list edit URL pattern"""
        url = reverse(
            "boards:list_edit", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/lists/123e4567-e89b-12d3-a456-426614174000/edit/"
        assert resolve(url).func == views.list_edit

    def test_list_delete_url(self):
        """Test the list delete URL pattern"""
        url = reverse(
            "boards:list_delete", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/lists/123e4567-e89b-12d3-a456-426614174000/delete/"
        assert resolve(url).func == views.list_delete

    def test_list_reorder_url(self):
        """Test the list reorder URL pattern"""
        url = reverse("boards:list_reorder")
        assert url == "/lists/reorder/"
        assert resolve(url).func == views.list_reorder

    def test_card_create_url(self):
        """Test the card create URL pattern"""
        url = reverse(
            "boards:card_create",
            kwargs={"list_id": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/lists/123e4567-e89b-12d3-a456-426614174000/cards/create/"
        assert resolve(url).func == views.card_create

    def test_card_detail_url(self):
        """Test the card detail URL pattern"""
        url = reverse(
            "boards:card_detail", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/"
        assert resolve(url).func == views.card_detail

    def test_card_edit_url(self):
        """Test the card edit URL pattern"""
        url = reverse(
            "boards:card_edit", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/edit/"
        assert resolve(url).func == views.card_edit

    def test_card_delete_url(self):
        """Test the card delete URL pattern"""
        url = reverse(
            "boards:card_delete", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/delete/"
        assert resolve(url).func == views.card_delete

    def test_card_move_url(self):
        """Test the card move URL pattern"""
        url = reverse(
            "boards:card_move", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/move/"
        assert resolve(url).func == views.card_move

    def test_card_reorder_url(self):
        """Test the card reorder URL pattern"""
        url = reverse("boards:card_reorder")
        assert url == "/cards/reorder/"
        assert resolve(url).func == views.card_reorder

    def test_card_toggle_complete_url(self):
        """Test the card toggle complete URL pattern"""
        url = reverse(
            "boards:card_toggle_complete",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/toggle-complete/"
        assert resolve(url).func == views.card_toggle_complete

    def test_label_create_url(self):
        """Test the label create URL pattern"""
        url = reverse("boards:label_create", kwargs={"board_slug": "test-board"})
        assert url == "/boards/test-board/labels/create/"
        assert resolve(url).func == views.label_create

    def test_label_edit_url(self):
        """Test the label edit URL pattern"""
        url = reverse(
            "boards:label_edit", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/labels/123e4567-e89b-12d3-a456-426614174000/edit/"
        assert resolve(url).func == views.label_edit

    def test_label_delete_url(self):
        """Test the label delete URL pattern"""
        url = reverse(
            "boards:label_delete", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/labels/123e4567-e89b-12d3-a456-426614174000/delete/"
        assert resolve(url).func == views.label_delete

    def test_card_add_label_url(self):
        """Test the card add label URL pattern"""
        url = reverse(
            "boards:card_add_label",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/labels/add/"
        assert resolve(url).func == views.card_add_label

    def test_card_remove_label_url(self):
        """Test the card remove label URL pattern"""
        url = reverse(
            "boards:card_remove_label",
            kwargs={
                "pk": "123e4567-e89b-12d3-a456-426614174000",
                "label_id": "123e4567-e89b-12d3-a456-426614174001",
            },
        )
        assert (
            url
            == "/cards/123e4567-e89b-12d3-a456-426614174000/labels/remove/123e4567-e89b-12d3-a456-426614174001/"
        )
        assert resolve(url).func == views.card_remove_label

    def test_comment_create_url(self):
        """Test the comment create URL pattern"""
        url = reverse(
            "boards:comment_create",
            kwargs={"card_id": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/comments/create/"
        assert resolve(url).func == views.comment_create

    def test_comment_edit_url(self):
        """Test the comment edit URL pattern"""
        url = reverse(
            "boards:comment_edit", kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"}
        )
        assert url == "/comments/123e4567-e89b-12d3-a456-426614174000/edit/"
        assert resolve(url).func == views.comment_edit

    def test_comment_delete_url(self):
        """Test the comment delete URL pattern"""
        url = reverse(
            "boards:comment_delete",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/comments/123e4567-e89b-12d3-a456-426614174000/delete/"
        assert resolve(url).func == views.comment_delete

    def test_attachment_upload_url(self):
        """Test the attachment upload URL pattern"""
        url = reverse(
            "boards:attachment_upload",
            kwargs={"card_id": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/attachments/upload/"
        assert resolve(url).func == views.attachment_upload

    def test_attachment_delete_url(self):
        """Test the attachment delete URL pattern"""
        url = reverse(
            "boards:attachment_delete",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/attachments/123e4567-e89b-12d3-a456-426614174000/delete/"
        assert resolve(url).func == views.attachment_delete

    def test_register_url(self):
        """Test the register URL pattern"""
        url = reverse("boards:register")
        assert url == "/register/"
        assert resolve(url).func == views.register

    def test_profile_url(self):
        """Test the profile URL pattern"""
        url = reverse("boards:profile")
        assert url == "/profile/"
        assert resolve(url).func == views.profile

    def test_board_add_member_url(self):
        """Test the board add member URL pattern"""
        url = reverse("boards:board_add_member", kwargs={"slug": "test-board"})
        assert url == "/boards/test-board/members/add/"
        assert resolve(url).func == views.board_add_member

    def test_board_remove_member_url(self):
        """Test the board remove member URL pattern"""
        url = reverse(
            "boards:board_remove_member", kwargs={"slug": "test-board", "user_id": 1}
        )
        assert url == "/boards/test-board/members/remove/1/"
        assert resolve(url).func == views.board_remove_member

    def test_card_add_member_url(self):
        """Test the card add member URL pattern"""
        url = reverse(
            "boards:card_add_member",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000"},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/members/add/"
        assert resolve(url).func == views.card_add_member

    def test_card_remove_member_url(self):
        """Test the card remove member URL pattern"""
        url = reverse(
            "boards:card_remove_member",
            kwargs={"pk": "123e4567-e89b-12d3-a456-426614174000", "user_id": 1},
        )
        assert url == "/cards/123e4567-e89b-12d3-a456-426614174000/members/remove/1/"
        assert resolve(url).func == views.card_remove_member
