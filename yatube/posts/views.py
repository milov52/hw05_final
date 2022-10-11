from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_page_obj


def index(request):
    posts = Post.objects.select_related("group")

    template = "posts/index.html"
    context = {"page_obj": get_page_obj(request, posts)}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts
    context = {"group": group, "page_obj": get_page_obj(request, posts.all())}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts
    following = False
    if (
        request.user.is_authenticated
        and Post.objects.filter(author__following__user=request.user).exists()
    ):
        following = True

    context = {
        "author": author,
        "page_obj": get_page_obj(request, posts.all()),
        "following": following,
    }

    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    comments = post.comments
    form = CommentForm(request.POST or None)

    context = {"post": post, "comments": comments.all(), "form": form}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    post = Post(author=request.user)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect("posts:profile", request.user.username)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    is_form_edit = True
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect("posts:post_detail", post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if not form.is_valid():
        context = {"form": form, "is_edit": is_form_edit, "post": post}
        return render(request, "posts/create_post.html", context)

    form.save()
    return redirect("posts:post_detail", post_id)


@login_required()
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {"page_obj": get_page_obj(request, posts)}

    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower_list = Follow.objects.filter(user=request.user, author=author)

    if follower_list.exists() or request.user == author:
        return redirect("posts:index")

    Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)

    following_list = Follow.objects.filter(user=request.user, author=author)

    if not following_list.exists():
        redirect("posts:index")

    following_list.delete()
    return redirect("posts:profile", username=username)
