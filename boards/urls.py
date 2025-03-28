from django.urls import path

from . import views

app_name = "boards"

urlpatterns = [
    # Home view
    path("", views.home, name="home"),
    # Board views
    path("boards/", views.board_list, name="board_list"),
    path("boards/create/", views.board_create, name="board_create"),
    path("boards/<slug:slug>/", views.board_detail, name="board_detail"),
    path("boards/<slug:slug>/edit/", views.board_edit, name="board_edit"),
    path("boards/<slug:slug>/delete/", views.board_delete, name="board_delete"),
    # List views
    path("boards/<slug:slug>/lists/create/", views.list_create, name="list_create"),
    path("lists/<uuid:pk>/edit/", views.list_edit, name="list_edit"),
    path("lists/<uuid:pk>/delete/", views.list_delete, name="list_delete"),
    path("lists/reorder/", views.list_reorder, name="list_reorder"),
    # Card views
    path("lists/<uuid:list_id>/cards/create/", views.card_create, name="card_create"),
    path("cards/<uuid:pk>/", views.card_detail, name="card_detail"),
    path("cards/<uuid:pk>/edit/", views.card_edit, name="card_edit"),
    path("cards/<uuid:pk>/delete/", views.card_delete, name="card_delete"),
    path("cards/<uuid:pk>/move/", views.card_move, name="card_move"),
    path("cards/reorder/", views.card_reorder, name="card_reorder"),
    path(
        "cards/<uuid:pk>/toggle-complete/",
        views.card_toggle_complete,
        name="card_toggle_complete",
    ),
    # Label views
    path(
        "boards/<slug:board_slug>/labels/create/",
        views.label_create,
        name="label_create",
    ),
    path("labels/<uuid:pk>/edit/", views.label_edit, name="label_edit"),
    path("labels/<uuid:pk>/delete/", views.label_delete, name="label_delete"),
    path("cards/<uuid:pk>/labels/add/", views.card_add_label, name="card_add_label"),
    path(
        "cards/<uuid:pk>/labels/remove/<uuid:label_id>/",
        views.card_remove_label,
        name="card_remove_label",
    ),
    # Comment views
    path(
        "cards/<uuid:card_id>/comments/create/",
        views.comment_create,
        name="comment_create",
    ),
    path("comments/<uuid:pk>/edit/", views.comment_edit, name="comment_edit"),
    path("comments/<uuid:pk>/delete/", views.comment_delete, name="comment_delete"),
    # Attachment views
    path(
        "cards/<uuid:card_id>/attachments/upload/",
        views.attachment_upload,
        name="attachment_upload",
    ),
    path(
        "attachments/<uuid:pk>/delete/",
        views.attachment_delete,
        name="attachment_delete",
    ),
    # User management
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path(
        "boards/<slug:slug>/members/add/",
        views.board_add_member,
        name="board_add_member",
    ),
    path(
        "boards/<slug:slug>/members/remove/<int:user_id>/",
        views.board_remove_member,
        name="board_remove_member",
    ),
    path("cards/<uuid:pk>/members/add/", views.card_add_member, name="card_add_member"),
    path(
        "cards/<uuid:pk>/members/remove/<int:user_id>/",
        views.card_remove_member,
        name="card_remove_member",
    ),
]
