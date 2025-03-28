import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from boards.models import Attachment, Board, Card, Comment, Label, List


# Authentication views
def register(request):
    """Register a new user"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully. You can now log in."
            )
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "auth/register.html", {"form": form})


@login_required
def profile(request):
    """View and edit user profile"""
    user = request.user
    boards = Board.objects.filter(owner=user)
    member_boards = user.member_boards.all()

    context = {
        "user": user,
        "boards": boards,
        "member_boards": member_boards,
    }

    return render(request, "boards/profile.html", context)


# Board views
@login_required
def board_list(request):
    """Display all boards the user has access to"""
    user = request.user
    owned_boards = Board.objects.filter(owner=user)
    member_boards = user.member_boards.all()

    context = {
        "owned_boards": owned_boards,
        "member_boards": member_boards,
    }

    return render(request, "boards/board_list.html", context)


@login_required
def board_create(request):
    """Create a new board"""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        background_color = request.POST.get("background_color", "#0079BF")

        if title:
            board = Board.objects.create(
                title=title,
                description=description,
                background_color=background_color,
                owner=request.user,
            )

            # Create default lists for the new board
            List.objects.create(title="To Do", board=board, position=1)
            List.objects.create(title="In Progress", board=board, position=2)
            List.objects.create(title="Done", board=board, position=3)

            messages.success(request, f'Board "{title}" created successfully.')
            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Title is required.")

    return render(request, "boards/board_create.html")


@login_required
def board_detail(request, slug):
    """Display a board and its lists and cards"""
    board = get_object_or_404(Board, slug=slug)

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    lists = board.lists.all().prefetch_related("cards")
    labels = board.labels.all()

    context = {
        "board": board,
        "lists": lists,
        "labels": labels,
    }

    return render(request, "boards/board_detail.html", context)


@login_required
def board_edit(request, slug):
    """Edit a board"""
    board = get_object_or_404(Board, slug=slug)

    # Check if user is the owner
    if board.owner != request.user:
        messages.error(request, "Only the board owner can edit the board.")
        return redirect("boards:board_detail", slug=board.slug)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        background_color = request.POST.get("background_color", board.background_color)

        if title:
            board.title = title
            board.description = description
            board.background_color = background_color
            board.save()

            messages.success(request, f'Board "{title}" updated successfully.')
            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Title is required.")

    context = {
        "board": board,
    }

    return render(request, "boards/board_edit.html", context)


@login_required
def board_delete(request, slug):
    """Delete a board"""
    board = get_object_or_404(Board, slug=slug)

    # Check if user is the owner
    if board.owner != request.user:
        messages.error(request, "Only the board owner can delete the board.")
        return redirect("boards:board_detail", slug=board.slug)

    if request.method == "POST":
        board_title = board.title
        board.delete()
        messages.success(request, f'Board "{board_title}" deleted successfully.')
        return redirect("boards:board_list")

    context = {
        "board": board,
    }

    return render(request, "boards/board_delete.html", context)


@login_required
def board_add_member(request, slug):
    """Add a member to a board"""
    board = get_object_or_404(Board, slug=slug)

    # Check if user is the owner
    if board.owner != request.user:
        messages.error(request, "Only the board owner can add members.")
        return redirect("boards:board_detail", slug=board.slug)

    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.get(username=username)

            # Check if user is already a member
            if user == board.owner:
                messages.error(request, "The owner is already a member of the board.")
            elif board.members.filter(id=user.id).exists():
                messages.error(
                    request, f"{username} is already a member of this board."
                )
            else:
                board.members.add(user)
                messages.success(
                    request, f"{username} added to the board successfully."
                )

                if request.htmx:
                    context = {"board": board, "members": board.members.all()}
                    return render(
                        request, "boards/partials/board_members.html", context
                    )

                return redirect("boards:board_detail", slug=board.slug)
        except User.DoesNotExist:
            messages.error(request, f"User {username} does not exist.")

    if request.htmx:
        return render(request, "boards/partials/add_member_form.html", {"board": board})

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def board_remove_member(request, slug, user_id):
    """Remove a member from a board"""
    board = get_object_or_404(Board, slug=slug)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if the current user is the owner or the member removing themselves
    if board.owner != request.user and request.user.id != user_id:
        messages.error(
            request, "You don't have permission to remove members from this board."
        )
        return redirect("boards:board_detail", slug=board.slug)

    if request.method == "POST":
        # Remove user from board members
        board.members.remove(user_to_remove)

        # Also remove user from all card assignments in this board
        for list_obj in board.lists.all():
            for card in list_obj.cards.all():
                card.members.remove(user_to_remove)

        messages.success(
            request, f"{user_to_remove.username} removed from the board successfully."
        )

        if request.htmx:
            context = {"board": board, "members": board.members.all()}
            return render(request, "boards/partials/board_members.html", context)

    return redirect("boards:board_detail", slug=board.slug)


# List views
@login_required
def list_create(request, slug):
    """Create a new list in a board"""
    board = get_object_or_404(Board, slug=slug)

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        title = request.POST.get("title")

        if title:
            # Get the highest position and add 1
            max_position = board.lists.aggregate(Max("position"))["position__max"] or 0

            list_obj = List.objects.create(
                title=title, board=board, position=max_position + 1
            )

            messages.success(request, f'List "{title}" created successfully.')

            if request.htmx:
                return render(
                    request,
                    "boards/partials/list.html",
                    {"list": list_obj, "board": board},
                )

            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Title is required.")

    if request.htmx:
        return render(
            request, "boards/partials/list_create_form.html", {"board": board}
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def list_edit(request, pk):
    """Edit a list"""
    list_obj = get_object_or_404(List, pk=pk)
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        title = request.POST.get("title")

        if title:
            list_obj.title = title
            list_obj.save()

            messages.success(request, f'List "{title}" updated successfully.')

            if request.htmx:
                return render(
                    request,
                    "boards/partials/list_header.html",
                    {"list": list_obj, "board": board},
                )

            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Title is required.")

    if request.htmx:
        return render(
            request,
            "boards/partials/list_edit_form.html",
            {"list": list_obj, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def list_delete(request, pk):
    """Delete a list"""
    list_obj = get_object_or_404(List, pk=pk)
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        list_title = list_obj.title
        list_obj.delete()

        # Reorder remaining lists
        for i, list_item in enumerate(board.lists.all().order_by("position")):
            list_item.position = i + 1
            list_item.save()

        messages.success(request, f'List "{list_title}" deleted successfully.')

        if request.htmx:
            return HttpResponse("")

        return redirect("boards:board_detail", slug=board.slug)

    if request.htmx:
        return render(
            request,
            "boards/partials/list_delete_confirm.html",
            {"list": list_obj, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
@require_POST
def list_reorder(request):
    """Reorder lists in a board using AJAX"""
    try:
        data = json.loads(request.body)
        board_slug = data.get("board_slug")
        list_orders = data.get("list_orders", [])

        board = get_object_or_404(Board, slug=board_slug)

        # Check if user has access to the board
        if (
            board.owner != request.user
            and not board.members.filter(id=request.user.id).exists()
        ):
            return JsonResponse(
                {"error": "You don't have access to this board."}, status=403
            )

        # Update list positions
        for order_data in list_orders:
            list_id = order_data.get("id")
            position = order_data.get("position")

            if list_id and position is not None:
                try:
                    list_obj = List.objects.get(pk=list_id, board=board)
                    list_obj.position = position
                    list_obj.save()
                except List.DoesNotExist:
                    pass

        return JsonResponse({"status": "success"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Card views
@login_required
def card_create(request, list_id):
    """Create a new card in a list"""
    list_obj = get_object_or_404(List, pk=list_id)
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        title = request.POST.get("title")

        if title:
            # Get the highest position and add 1
            max_position = (
                list_obj.cards.aggregate(Max("position"))["position__max"] or 0
            )

            card = Card.objects.create(
                title=title, list=list_obj, position=max_position + 1
            )

            messages.success(request, f'Card "{title}" created successfully.')

            if request.htmx:
                return render(
                    request, "boards/partials/card.html", {"card": card, "board": board}
                )

            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Title is required.")

    if request.htmx:
        return render(
            request,
            "boards/partials/card_create_form.html",
            {"list": list_obj, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def card_detail(request, pk):
    """View card details"""
    card = get_object_or_404(Card, pk=pk)
    list_obj = card.list
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    comments = card.comments.all().order_by("-created_at")
    attachments = card.attachments.all()
    labels = board.labels.all()
    card_labels = card.labels.all()
    members = board.members.all()
    card_members = card.members.all()

    context = {
        "card": card,
        "list": list_obj,
        "board": board,
        "comments": comments,
        "attachments": attachments,
        "labels": labels,
        "card_labels": card_labels,
        "members": members,
        "card_members": card_members,
    }

    if request.htmx:
        return render(request, "boards/partials/card_detail.html", context)

    return render(request, "boards/card_detail.html", context)


@login_required
def card_edit(request, pk):
    """Edit a card"""
    card = get_object_or_404(Card, pk=pk)
    list_obj = card.list
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        due_date = request.POST.get("due_date", None)

        if title:
            card.title = title
            card.description = description
            card.due_date = due_date
            card.save()

            messages.success(request, f'Card "{title}" updated successfully.')

            if request.htmx:
                if "card_title" in request.POST:
                    return render(
                        request, "boards/partials/card_title.html", {"card": card}
                    )
                elif "card_description" in request.POST:
                    return render(
                        request, "boards/partials/card_description.html", {"card": card}
                    )
                else:
                    return redirect("boards:card_detail", pk=card.pk)

            return redirect("boards:card_detail", pk=card.pk)
        else:
            messages.error(request, "Title is required.")

    if request.htmx:
        if "edit_title" in request.GET:
            return render(
                request, "boards/partials/card_edit_title_form.html", {"card": card}
            )
        elif "edit_description" in request.GET:
            return render(
                request,
                "boards/partials/card_edit_description_form.html",
                {"card": card},
            )
        elif "edit_due_date" in request.GET:
            return render(
                request, "boards/partials/card_edit_due_date_form.html", {"card": card}
            )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def card_delete(request, pk):
    """Delete a card"""
    card = get_object_or_404(Card, pk=pk)
    list_obj = card.list
    board = list_obj.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        card_title = card.title
        card.delete()

        # Reorder remaining cards
        for i, card_item in enumerate(list_obj.cards.all().order_by("position")):
            card_item.position = i + 1
            card_item.save()

        messages.success(request, f'Card "{card_title}" deleted successfully.')

        if request.htmx:
            return HttpResponse("")

        return redirect("boards:board_detail", slug=board.slug)

    if request.htmx:
        return render(
            request,
            "boards/partials/card_delete_confirm.html",
            {"card": card, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
@require_POST
def card_move(request, pk):
    """Move a card to another list"""
    card = get_object_or_404(Card, pk=pk)
    old_list = card.list
    board = old_list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    list_id = request.POST.get("list_id")
    position = request.POST.get("position")

    if list_id and position:
        try:
            new_list = List.objects.get(pk=list_id, board=board)
            position = int(position)

            # Update card
            card.list = new_list
            card.position = position
            card.save()

            # Reorder cards in the old list
            for i, card_item in enumerate(old_list.cards.all().order_by("position")):
                card_item.position = i + 1
                card_item.save()

            # Reorder cards in the new list
            for i, card_item in enumerate(new_list.cards.all().order_by("position")):
                if card_item.id != card.id:  # Skip the moved card
                    if i + 1 >= position:
                        card_item.position = i + 2  # Make room for the moved card
                    else:
                        card_item.position = i + 1
                    card_item.save()

            if request.htmx:
                return render(
                    request, "boards/partials/card.html", {"card": card, "board": board}
                )

            return redirect("boards:board_detail", slug=board.slug)
        except (List.DoesNotExist, ValueError):
            messages.error(request, "Invalid list or position.")
    else:
        messages.error(request, "List and position are required.")

    return redirect("boards:board_detail", slug=board.slug)


@login_required
@require_POST
def card_reorder(request):
    """Reorder cards in a list using AJAX"""
    try:
        data = json.loads(request.body)
        list_id = data.get("list_id")
        card_orders = data.get("card_orders", [])

        list_obj = get_object_or_404(List, pk=list_id)
        board = list_obj.board

        # Check if user has access to the board
        if (
            board.owner != request.user
            and not board.members.filter(id=request.user.id).exists()
        ):
            return JsonResponse(
                {"error": "You don't have access to this board."}, status=403
            )

        # Update card positions
        for order_data in card_orders:
            card_id = order_data.get("id")
            position = order_data.get("position")

            if card_id and position is not None:
                try:
                    card = Card.objects.get(pk=card_id, list=list_obj)
                    card.position = position
                    card.save()
                except Card.DoesNotExist:
                    pass

        return JsonResponse({"status": "success"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def card_toggle_complete(request, pk):
    """Toggle card completion status"""
    card = get_object_or_404(Card, pk=pk)
    board = card.list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    card.is_completed = not card.is_completed
    card.save()

    if request.htmx:
        return render(
            request, "boards/partials/card_complete_status.html", {"card": card}
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def card_add_member(request, pk):
    """Add a member to a card"""
    card = get_object_or_404(Card, pk=pk)
    board = card.list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        user_id = request.POST.get("user_id")

        if user_id:
            try:
                user = User.objects.get(pk=user_id)

                # Check if user is a board member
                if user == board.owner or board.members.filter(id=user.id).exists():
                    # Check if user is already assigned to the card
                    if card.members.filter(id=user.id).exists():
                        messages.error(
                            request,
                            f"{user.username} is already assigned to this card.",
                        )
                    else:
                        card.members.add(user)
                        messages.success(
                            request,
                            f"{user.username} assigned to the card successfully.",
                        )
                else:
                    messages.error(
                        request, f"{user.username} is not a member of this board."
                    )

                if request.htmx:
                    return render(
                        request,
                        "boards/partials/card_members.html",
                        {"card": card, "board": board},
                    )
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")

    if request.htmx:
        board_members = list(board.members.all()) + [board.owner]
        return render(
            request,
            "boards/partials/card_add_member_form.html",
            {"card": card, "board": board, "board_members": board_members},
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def card_remove_member(request, pk, user_id):
    """Remove a member from a card"""
    card = get_object_or_404(Card, pk=pk)
    board = card.list.board
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        card.members.remove(user_to_remove)
        messages.success(
            request, f"{user_to_remove.username} removed from the card successfully."
        )

        if request.htmx:
            return render(
                request,
                "boards/partials/card_members.html",
                {"card": card, "board": board},
            )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def card_add_label(request, pk):
    """Add a label to a card"""
    card = get_object_or_404(Card, pk=pk)
    board = card.list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        label_id = request.POST.get("label_id")

        if label_id:
            try:
                label = Label.objects.get(pk=label_id, board=board)

                # Check if label is already added to the card
                if card.labels.filter(id=label.id).exists():
                    messages.error(
                        request, f"Label '{label.name}' is already added to this card."
                    )
                else:
                    card.labels.add(label)
                    messages.success(
                        request, f"Label '{label.name}' added to the card successfully."
                    )

                if request.htmx:
                    return render(
                        request,
                        "boards/partials/card_labels.html",
                        {"card": card, "board": board},
                    )
            except Label.DoesNotExist:
                messages.error(request, "Label does not exist.")

    if request.htmx:
        board_labels = board.labels.all()
        return render(
            request,
            "boards/partials/card_add_label_form.html",
            {"card": card, "board": board, "board_labels": board_labels},
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def card_remove_label(request, pk, label_id):
    """Remove a label from a card"""
    card = get_object_or_404(Card, pk=pk)
    board = card.list.board
    label = get_object_or_404(Label, id=label_id, board=board)

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        card.labels.remove(label)
        messages.success(
            request, f"Label '{label.name}' removed from the card successfully."
        )

        if request.htmx:
            return render(
                request,
                "boards/partials/card_labels.html",
                {"card": card, "board": board},
            )

    return redirect("boards:card_detail", pk=card.pk)


# Comment views
@login_required
def comment_create(request, card_id):
    """Add a comment to a card"""
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        text = request.POST.get("text")

        if text:
            comment = Comment.objects.create(text=text, card=card, author=request.user)

            messages.success(request, "Comment added successfully.")

            if request.htmx:
                return render(
                    request,
                    "boards/partials/comment.html",
                    {"comment": comment, "card": card, "board": board},
                )

            return redirect("boards:card_detail", pk=card.pk)
        else:
            messages.error(request, "Comment text is required.")

    if request.htmx:
        return render(
            request, "boards/partials/comment_form.html", {"card": card, "board": board}
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def comment_edit(request, pk):
    """Edit a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    card = comment.card
    board = card.list.board

    # Check if user is the author or board owner
    if comment.author != request.user and board.owner != request.user:
        messages.error(request, "You can only edit your own comments.")
        return redirect("boards:card_detail", pk=card.pk)

    if request.method == "POST":
        text = request.POST.get("text")

        if text:
            comment.text = text
            comment.save()

            messages.success(request, "Comment updated successfully.")

            if request.htmx:
                return render(
                    request,
                    "boards/partials/comment.html",
                    {"comment": comment, "card": card, "board": board},
                )

            return redirect("boards:card_detail", pk=card.pk)
        else:
            messages.error(request, "Comment text is required.")

    if request.htmx:
        return render(
            request,
            "boards/partials/comment_edit_form.html",
            {"comment": comment, "card": card, "board": board},
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def comment_delete(request, pk):
    """Delete a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    card = comment.card
    board = card.list.board

    # Check if user is the author or board owner
    if comment.author != request.user and board.owner != request.user:
        messages.error(request, "You can only delete your own comments.")
        return redirect("boards:card_detail", pk=card.pk)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")

        if request.htmx:
            return HttpResponse("")

        return redirect("boards:card_detail", pk=card.pk)

    if request.htmx:
        return render(
            request,
            "boards/partials/comment_delete_confirm.html",
            {"comment": comment, "card": card, "board": board},
        )

    return redirect("boards:card_detail", pk=card.pk)


# Attachment views
@login_required
def attachment_upload(request, card_id):
    """Upload an attachment to a card"""
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        file = request.FILES.get("file")
        name = request.POST.get("name", "")

        if file:
            # Use the file name if no name is provided
            if not name:
                name = file.name

            attachment = Attachment.objects.create(
                file=file, name=name, card=card, uploaded_by=request.user
            )

            messages.success(request, f"Attachment '{name}' uploaded successfully.")

            if request.htmx:
                return render(
                    request,
                    "boards/partials/attachment.html",
                    {"attachment": attachment, "card": card, "board": board},
                )

            return redirect("boards:card_detail", pk=card.pk)
        else:
            messages.error(request, "No file was uploaded.")

    if request.htmx:
        return render(
            request,
            "boards/partials/attachment_form.html",
            {"card": card, "board": board},
        )

    return redirect("boards:card_detail", pk=card.pk)


@login_required
def attachment_delete(request, pk):
    """Delete an attachment"""
    attachment = get_object_or_404(Attachment, pk=pk)
    card = attachment.card
    board = card.list.board

    # Check if user is the uploader or board owner
    if attachment.uploaded_by != request.user and board.owner != request.user:
        messages.error(request, "You can only delete your own attachments.")
        return redirect("boards:card_detail", pk=card.pk)

    if request.method == "POST":
        attachment_name = attachment.name
        attachment.delete()
        messages.success(
            request, f"Attachment '{attachment_name}' deleted successfully."
        )

        if request.htmx:
            return HttpResponse("")

        return redirect("boards:card_detail", pk=card.pk)

    if request.htmx:
        return render(
            request,
            "boards/partials/attachment_delete_confirm.html",
            {"attachment": attachment, "card": card, "board": board},
        )

    return redirect("boards:card_detail", pk=card.pk)


# Label views
@login_required
def label_create(request, board_slug):
    """Create a new label for a board"""
    board = get_object_or_404(Board, slug=board_slug)

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color", "#0079BF")

        if name:
            label = Label.objects.create(name=name, color=color, board=board)

            messages.success(request, f"Label '{name}' created successfully.")

            if request.htmx:
                return render(
                    request,
                    "boards/partials/label.html",
                    {"label": label, "board": board},
                )

            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Label name is required.")

    if request.htmx:
        return render(request, "boards/partials/label_form.html", {"board": board})

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def label_edit(request, pk):
    """Edit a label"""
    label = get_object_or_404(Label, pk=pk)
    board = label.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color", label.color)

        if name:
            label.name = name
            label.color = color
            label.save()

            messages.success(request, f"Label '{name}' updated successfully.")

            if request.htmx:
                return render(
                    request,
                    "boards/partials/label.html",
                    {"label": label, "board": board},
                )

            return redirect("boards:board_detail", slug=board.slug)
        else:
            messages.error(request, "Label name is required.")

    if request.htmx:
        return render(
            request,
            "boards/partials/label_edit_form.html",
            {"label": label, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


@login_required
def label_delete(request, pk):
    """Delete a label"""
    label = get_object_or_404(Label, pk=pk)
    board = label.board

    # Check if user has access to the board
    if (
        board.owner != request.user
        and not board.members.filter(id=request.user.id).exists()
    ):
        messages.error(request, "You don't have access to this board.")
        return redirect("boards:board_list")

    if request.method == "POST":
        label_name = label.name

        # Remove the label from all cards
        for list_obj in board.lists.all():
            for card in list_obj.cards.all():
                card.labels.remove(label)

        label.delete()
        messages.success(request, f"Label '{label_name}' deleted successfully.")

        if request.htmx:
            return HttpResponse("")

        return redirect("boards:board_detail", slug=board.slug)

    if request.htmx:
        return render(
            request,
            "boards/partials/label_delete_confirm.html",
            {"label": label, "board": board},
        )

    return redirect("boards:board_detail", slug=board.slug)


# Home view
def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect("boards:board_list")

    return render(request, "boards/home.html")
