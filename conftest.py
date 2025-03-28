import os
import sys

import django
import pytest
from django.contrib.auth.models import User

from boards.models import Attachment, Board, Card, Comment, Label, List

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trelleo.settings")

# Set ALLOWED_HOSTS environment variable to include 'testserver'
os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,testserver"

django.setup()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="password123"
    )


@pytest.fixture
def admin_user(db):
    """Create an admin test user"""
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def board(db, user):
    """Create a test board"""
    return Board.objects.create(
        title="Test Board",
        description="This is a test board",
        owner=user,
        background_color="#0079BF",
    )


@pytest.fixture
def list_obj(db, board):
    """Create a test list"""
    return List.objects.create(title="Test List", board=board, position=1)


@pytest.fixture
def card(db, list_obj):
    """Create a test card"""
    return Card.objects.create(
        title="Test Card", description="This is a test card", list=list_obj, position=1
    )


@pytest.fixture
def label(db, board):
    """Create a test label"""
    return Label.objects.create(name="Test Label", color="#FF0000", board=board)


@pytest.fixture
def comment(db, card, user):
    """Create a test comment"""
    return Comment.objects.create(text="This is a test comment", card=card, author=user)


@pytest.fixture
def attachment(db, card, user):
    """Create a test attachment"""
    return Attachment.objects.create(
        name="Test Attachment", card=card, uploaded_by=user, file="test.txt"
    )
