from django.core.paginator import Paginator

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by("-timestamp")

    # Paginate posts 10 per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    """
    Create a new post and save it to the database.

    If the content of the post is empty, render the index page with an error message.
    Otherwise, create a new Post object with the content and the current user as the author.
    Save the post to the database and redirect to the index page.

    This view is only accessible if the user is logged in.
    """
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip() == "":
            return render(request, "network/index.html", {
                "message": "Post cannot be empty."
            })
        post = Post(author=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def profile(request, username):
    """
    Displays the profile of the given user, including their posts and follower / following counts.

    If the current user is not authenticated, redirect to the index page.
    If the current user is authenticated but not following the given user, render the 'toggle_follow' form.
    If the current user is authenticated and following the given user, render the 'toggle_follow' form with the 'Unfollow' button.

    Args:
        request: The request object.
        username: The username of the user to display the profile of.

    Returns:
        A rendered HttpResponse containing the profile information.
    """
    profile_user = get_object_or_404(User, username=username)

    # All posts by this user (newest first)
    posts = Post.objects.filter(author=profile_user).order_by("-timestamp")

    # Paginate posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Follower / following counts
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    # Check if current user already follows this profile
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "page_obj": page_obj,
    })


@login_required
def toggle_follow(request, username):
    """
    Toggles the follow relation between the current user and the given user.

    Args:
        request: The request object.
        username: The username of the user to toggle the follow relation with.

    Returns:
        A rendered HttpResponse containing the profile information.
    """
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        return HttpResponseRedirect(reverse("profile", args=[username]))

    follow_relation, created = Follow.objects.get_or_create(
        follower=request.user,
        following=profile_user
    )
    if not created:
        # Already following -> unfollow
        follow_relation.delete()
    return HttpResponseRedirect(reverse("profile", args=[username]))


@login_required
def following(request):
    # Get all users the current user follows
    """
    Displays a feed of posts from all users that the current user follows.

    Returns:
        A rendered HttpResponse containing the followed users' posts.
    """
    followed_users = Follow.objects.filter(follower=request.user).values_list("following", flat=True)

    # Get posts from those users only
    posts = Post.objects.filter(author__in=followed_users).order_by("-timestamp")

    # Paginate
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
@csrf_exempt
def edit_post(request, post_id):
    """
    Edit a post by its ID.

    Only the author of the post can edit it, and the request must be a PUT request with a JSON body containing the new content of the post.

    Args:
        request: The request object.
        post_id: The ID of the post to edit.

    Returns:
        A rendered JsonResponse containing the new content of the post, or an error message if the request is invalid or the user is not authorized.
    """
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            new_content = data.get("content", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        # Security: only author can edit
        if post.author != request.user:
            return JsonResponse({"error": "Not authorized"}, status=403)

        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({
                "message": "Post updated successfully",
                "new_content": post.content
            })
        else:
            return JsonResponse({"error": "Content cannot be empty"}, status=400)

    return JsonResponse({"error": "PUT request required"}, status=400)
