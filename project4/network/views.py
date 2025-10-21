from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all()
    return render(request, "network/index.html", {
        "posts": posts
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


def profile(request, username):
    """
    Renders a profile page for a given user.

    Retrieves the user's posts, followers count, following count, and
    determines if the current user is following this profile.

    Args:
        request: The request object.
        username: The username of the user to render the profile for.

    Returns:
        A rendered HttpResponse containing the profile information.
    """
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user)

    # Followers and following counts
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    # Determine if current user follows this profile
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
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
    # Get all users that the current user follows
    followed_users = request.user.following.values_list("following", flat=True)

    # Get posts only from those users
    posts = Post.objects.filter(
        author__in=followed_users).order_by("-timestamp")

    return render(request, "network/following.html", {
        "posts": posts
    })
