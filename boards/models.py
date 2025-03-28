import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

# Create your models here.


class Board(models.Model):
    """Board model representing a project or workspace"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )
    members = models.ManyToManyField(User, related_name="member_boards", blank=True)
    background_color = models.CharField(max_length=50, default="#0079BF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Check if the slug already exists
            counter = 1
            original_slug = self.slug
            while Board.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Label(models.Model):
    """Label model for categorizing cards"""

    COLOR_CHOICES = [
        ("#61BD4F", "Green"),
        ("#F2D600", "Yellow"),
        ("#FF9F1A", "Orange"),
        ("#EB5A46", "Red"),
        ("#C377E0", "Purple"),
        ("#0079BF", "Blue"),
        ("#00C2E0", "Sky"),
        ("#51E898", "Lime"),
        ("#FF78CB", "Pink"),
        ("#344563", "Black"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, default="#0079BF")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="labels")

    def __str__(self):
        return self.name


class List(models.Model):
    """List model representing a column in a board"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.title


class Card(models.Model):
    """Card model representing a task or item in a list"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="cards")
    position = models.PositiveIntegerField(default=0)
    labels = models.ManyToManyField(Label, related_name="cards", blank=True)
    members = models.ManyToManyField(User, related_name="assigned_cards", blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model for card discussions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.card.title}"


class Attachment(models.Model):
    """Attachment model for files attached to cards"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/")
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attachments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
