# from django.contrib.auth import default_app_config
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):
        return self.username


class Posts(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through="PostsLikes", blank=True)

    class Meta:
        ordering = ['-created_at']
       
    def likes_count(self):
        return PostsLikes.objects.filter(posts=self.id, like_is_active=True).exclude(user=self.author).count()
    
    def __str__(self):
        return f"post {self.id} of {self.author.username}"


class PostsLikes(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)
    like_is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'network_posts_likes'
        constraints = [ 
            models.UniqueConstraint(fields=['user', 'posts'], name='liked'),
        ]

class Followers(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="followed")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="followers")
    is_followed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower'], name='following'),
        ]  
