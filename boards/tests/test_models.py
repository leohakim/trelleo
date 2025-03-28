import pytest
from django.utils.text import slugify

from boards.models import Attachment, Board, Card, Comment, Label, List


@pytest.mark.models
@pytest.mark.unit
class TestBoardModel:
    """Tests for the Board model"""

    def test_board_creation(self, board, user):
        """Test that a board can be created"""
        assert board.title == "Test Board"
        assert board.description == "This is a test board"
        assert board.owner == user
        assert board.background_color == "#0079BF"
        assert board.slug == slugify(board.title)

    def test_board_str_representation(self, board):
        """Test the string representation of a board"""
        assert str(board) == "Test Board"

    def test_board_slug_generation(self, db, user):
        """Test that a slug is automatically generated from the title"""
        board = Board.objects.create(title="My New Board", owner=user)
        assert board.slug == "my-new-board"

    def test_board_unique_slug(self, db, user, board):
        """Test that boards with the same title get unique slugs"""
        # Create a board with the same title
        board2 = Board.objects.create(title="Test Board", owner=user)
        assert board2.slug != board.slug
        assert board2.slug.startswith("test-board-")


@pytest.mark.models
@pytest.mark.unit
class TestListModel:
    """Tests for the List model"""

    def test_list_creation(self, list_obj, board):
        """Test that a list can be created"""
        assert list_obj.title == "Test List"
        assert list_obj.board == board
        assert list_obj.position == 1

    def test_list_str_representation(self, list_obj):
        """Test the string representation of a list"""
        assert str(list_obj) == "Test List"

    def test_list_ordering(self, db, board):
        """Test that lists are ordered by position"""
        List.objects.create(title="List 1", board=board, position=3)
        List.objects.create(title="List 2", board=board, position=1)
        List.objects.create(title="List 3", board=board, position=2)

        lists = List.objects.filter(board=board)
        assert lists[0].title == "List 2"  # position 1
        assert lists[1].title == "List 3"  # position 2
        assert lists[2].title == "List 1"  # position 3


@pytest.mark.models
@pytest.mark.unit
class TestCardModel:
    """Tests for the Card model"""

    def test_card_creation(self, card, list_obj):
        """Test that a card can be created"""
        assert card.title == "Test Card"
        assert card.description == "This is a test card"
        assert card.list == list_obj
        assert card.position == 1
        assert card.is_completed is False

    def test_card_str_representation(self, card):
        """Test the string representation of a card"""
        assert str(card) == "Test Card"

    def test_card_ordering(self, db, list_obj):
        """Test that cards are ordered by position"""
        Card.objects.create(title="Card 1", list=list_obj, position=3)
        Card.objects.create(title="Card 2", list=list_obj, position=1)
        Card.objects.create(title="Card 3", list=list_obj, position=2)

        cards = Card.objects.filter(list=list_obj)
        assert cards[0].title == "Card 2"  # position 1
        assert cards[1].title == "Card 3"  # position 2
        assert cards[2].title == "Card 1"  # position 3

    def test_card_completion(self, card):
        """Test that a card can be marked as completed"""
        assert card.is_completed is False

        card.is_completed = True
        card.save()

        updated_card = Card.objects.get(id=card.id)
        assert updated_card.is_completed is True


@pytest.mark.models
@pytest.mark.unit
class TestLabelModel:
    """Tests for the Label model"""

    def test_label_creation(self, label, board):
        """Test that a label can be created"""
        assert label.name == "Test Label"
        assert label.color == "#FF0000"
        assert label.board == board

    def test_label_str_representation(self, label):
        """Test the string representation of a label"""
        assert str(label) == "Test Label"

    def test_label_default_color(self, db, board):
        """Test that a label gets a default color if none is provided"""
        label = Label.objects.create(name="Default Color Label", board=board)
        assert label.color == "#0079BF"  # Default color


@pytest.mark.models
@pytest.mark.unit
class TestCommentModel:
    """Tests for the Comment model"""

    def test_comment_creation(self, comment, card, user):
        """Test that a comment can be created"""
        assert comment.text == "This is a test comment"
        assert comment.card == card
        assert comment.author == user
        assert comment.created_at is not None

    def test_comment_str_representation(self, comment):
        """Test the string representation of a comment"""
        assert str(comment) == "Comment by testuser on Test Card"

    def test_comment_ordering(self, db, card, user):
        """Test that comments are ordered by created_at"""
        # We can't easily test exact ordering with created_at timestamps in a unit test,
        # but we can test that the model has the correct Meta ordering
        assert Comment._meta.ordering == ["created_at"]


@pytest.mark.models
@pytest.mark.unit
class TestAttachmentModel:
    """Tests for the Attachment model"""

    def test_attachment_creation(self, attachment, card, user):
        """Test that an attachment can be created"""
        assert attachment.name == "Test Attachment"
        assert attachment.card == card
        assert attachment.uploaded_by == user
        assert attachment.created_at is not None
        assert attachment.file == "test.txt"

    def test_attachment_str_representation(self, attachment):
        """Test the string representation of an attachment"""
        assert str(attachment) == "Test Attachment"

    def test_attachment_ordering(self, db):
        """Test that attachments don't have explicit ordering"""
        # Attachments don't have explicit ordering in the model
        assert (
            not hasattr(Attachment._meta, "ordering") or Attachment._meta.ordering == []
        )
