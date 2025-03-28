from django.contrib import admin

from .models import Attachment, Board, Card, Comment, Label, List

# Register your models here.


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    list_filter = ("owner", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("title", "board", "position", "created_at")
    list_filter = ("board", "created_at")
    search_fields = ("title",)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "list",
        "position",
        "due_date",
        "is_completed",
        "created_at",
    )
    list_filter = ("list", "is_completed", "due_date", "created_at")
    search_fields = ("title", "description")
    filter_horizontal = ("labels", "members")


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "board")
    list_filter = ("board", "color")
    search_fields = ("name",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("card", "author", "created_at")
    list_filter = ("card", "author", "created_at")
    search_fields = ("text",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "card", "uploaded_by", "created_at")
    list_filter = ("card", "uploaded_by", "created_at")
    search_fields = ("name",)
