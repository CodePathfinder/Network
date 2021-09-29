
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user_profile/<int:pk>", views.user_profile, name="user_profile"),
    path("following", views.following, name="following"),
    path("follow_control/<int:pk>", views.follow_control, name="follow_control"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # API Routes
    path("post_update/<int:post_id>", views.post_update, name="post_update"),
    path("likes_update/<int:post_id>", views.likes_update, name="likes_update"),
]
