import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from network.form import NewPost
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator


from .models import User, Posts, Followers, PostsLikes


DEFAULT_NUMBER_OF_POSTS_PER_PAGE = 10


def index(request):

    if request.method == "POST":
        form = NewPost(request.POST)
        if form.is_valid():
            new_post = Posts(
                author = request.user,
                content=form.cleaned_data['content']
            )
            new_post.save()
            return redirect('index')
        else:
            post_form = NewPost(form)
    else:
        post_form = NewPost()

    posts = Posts.objects.all()

    # pagination has optional third argument - number of object on page (int), 
    # default=DEFAULT_NUMBER_OF_POSTS_PER_PAGE
    page = pagination(request, posts)

    context = {
        'post_form': post_form,
        'page_object': page
    }
    return render(request, "network/index.html", context)


def user_profile(request, pk):   

    if request.method == "POST":
        form = NewPost(request.POST)
        if form.is_valid():
            new_post = Posts(
                author = request.user,
                content=form.cleaned_data['content']
            )
            new_post.save()
            return redirect('user_profile', pk)
        else:
            post_form = NewPost(form)
    # processing GET request
    else:
        post_form = NewPost()
        
        # get all posts of the author
        posts = Posts.objects.filter(author__id=pk)
        
        # get all followers of the author
        followers = Followers.objects.filter(user__id=pk, is_followed=True)
        
        # verify if the author is followed by the current user
        relation = followers.filter(follower__id=request.user.id)
        
        # pagination has optional third argument - number of object on page (int), 
        # default=DEFAULT_NUMBER_OF_POSTS_PER_PAGE
        page = pagination(request, posts)

        context = {
            'post_form': post_form,
            'author': User.objects.filter(id=pk).first(),
            'page_object': page,
            'is_follower': relation.first().is_followed if relation.exists() else False,
            'followers_count': followers.count(),
            'follow_count': Followers.objects.filter(follower__id=pk, is_followed=True).count()
        }
        return render(request, "network/user_profile.html", context)


@login_required(login_url='login')
def follow_control(request, pk):   

    if request.method == "POST":
        author_id = int(request.POST["author_id"])
        
        # verify that posts author is not curent user:
        if author_id != pk or author_id == request.user.id:
            return HttpResponse('Bad Request', status=400)
        else:
            relation = Followers.objects.filter(user__id=pk, follower__id=request.user.id) 
            
            # update existing entry in 'followers' table
            if relation.exists():
                auth = relation.first()
                auth.is_followed = False if auth.is_followed else True
                auth.save()
            
            # create new entry in 'followers' table
            else:
                author = User.objects.get(id=pk)
                follower = User.objects.get(id=request.user.id)
                auth = Followers.objects.create(
                    user = author,
                    follower = follower,
                    is_followed = True
                )
            return redirect('user_profile', pk)
    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required(login_url='login')
def following(request):

    # get list of authors which are followed by the current user
    followed_authors = Followers.objects.filter(follower__id=request.user.id, is_followed=True).exclude(user__id=request.user.id)
    followed_users = [fa.user for fa in followed_authors]
    posts = Posts.objects.filter(author__in=followed_users)
    
    # pagination has optional third argument - number of object on page (int), 
    # default=DEFAULT_NUMBER_OF_POSTS_PER_PAGE
    page = pagination(request, posts)

    context = {
        'page_object': page
    }
    return render(request, "network/following.html", context)


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


@login_required(login_url='login')
@csrf_exempt
def post_update(request, post_id):

    if request.method == "POST":
        
        try:
            post = Posts.objects.get(id=post_id)
        except Posts.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        if request.user.id != post.author.id:
            return JsonResponse({"error": "Unauthorized request"}, status=403)

        else:
            data = json.loads(request.body)
            if data.get("updated_post") is not None:
                post.content = data["updated_post"]
            post.save()
            
            return JsonResponse({"content": post.content}, status=200)
    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required(login_url='login')
@csrf_exempt
def likes_update(request, post_id):
    
    post = Posts.objects.get(id=post_id)
    if post.author == request.user:
        pass
    elif post.likes.filter(id=request.user.id).exists():
        check_like_status = PostsLikes.objects.get(posts=post, user=request.user.id)  
        check_like_status.like_is_active = not check_like_status.like_is_active
        check_like_status.save()
    else:
        post.likes.add(request.user) 
    return JsonResponse({"likes_count": post.likes_count()}, status=200)


def pagination(request, objects_list, n=DEFAULT_NUMBER_OF_POSTS_PER_PAGE):

    paginator = Paginator(objects_list, n)

    # page number is extracted from GET dictionary of the request object, default value 1
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    return (page)
