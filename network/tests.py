from django.db.models import Max
from django.test import Client, TestCase

from .models import User, Posts, Followers, PostsLikes

# Create your tests here.
class NetworkTestCase(TestCase):

    def setUp(self):

        # Create users.
        u1 = User.objects.create(username="Alice", password="123")
        u2 = User.objects.create(username="Bob20", password="123")
        u3 = User.objects.create(username="DanBilan", password="123")
        u4 = User.objects.create(username="eva-cat", password="123")

        # Create posts.
        p1 = Posts.objects.create(author=u1, content="First post of Alice")
        p2 = Posts.objects.create(author=u1, content="Second post of Alice")
        p3 = Posts.objects.create(author=u2, content="First post of Bob")
        p4 = Posts.objects.create(author=u2, content="Second post of Bob")
        p5 = Posts.objects.create(author=u2, content="Third post of Bob")
        p6 = Posts.objects.create(author=u3, content="First post of Dan Bilan")
        p7 = Posts.objects.create(author=u3, content="Second post of Dan Bilan")
        p8 = Posts.objects.create(author=u3, content="Third post of Dan Bilan")
        p9 = Posts.objects.create(author=u3, content="Forth post of Dan Bilan")

        # Create likes.
        PostsLikes.objects.create(user = u1, posts = p6, like_is_active=True)        
        PostsLikes.objects.create(user = u2, posts = p6, like_is_active=True)
        PostsLikes.objects.create(user = u4, posts = p6, like_is_active=True)

# tests of model relationships

    def test_posts_count(self):
        user = User.objects.get(username="DanBilan")
        self.assertEqual(user.author.count(), 4)  

    def test_followers_count(self):
        u1 = User.objects.get(username="DanBilan")
        u2 = User.objects.get(username="eva-cat")
        u3 = User.objects.get(username="Bob20")
        u4 = User.objects.get(username="Alice")
        Followers.objects.create(user=u1, follower=u2)
        Followers.objects.create(user=u3, follower=u2)
        Followers.objects.create(user=u4, follower=u2)
        Followers.objects.create(user=u1, follower=u4)
        followers = Followers.objects.filter(user = u1, is_followed=True)
        followed = Followers.objects.filter(follower = u2, is_followed=True)
        self.assertEqual(followers.count(), 2)
        self.assertEqual(followed.count(), 3)

    # def test_invalid_follower(self):
    #     u1 = User.objects.get(username="DanBilan")
    #     Followers.objects.create(user=u1, follower=u1)
    #     followers = Followers.objects.filter(user = u1, is_followed=True)
    #     c = Client()
    #     response = c.get("/following/")
    #     print(response)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.context["is_follower"])
    #     self.assertEqual(followers.count(), 0)

    def test_invalid_like(self):
        user = User.objects.get(username="DanBilan")
        post = Posts.objects.get(content="Second post of Dan Bilan")
        PostsLikes.objects.create(user = user, posts = post)       
        self.assertEqual(post.likes_count(), 0)
    
# test of class Posts method

    def test_likes_count(self):
        post = Posts.objects.get(content="First post of Dan Bilan")
        self.assertEqual(post.likes_count(), 3)


# tests of response

    def test_user_profile(self):
        user = User.objects.get(username="Alice")
        follower = User.objects.get(username="Bob20")
        Followers.objects.create(user=user, follower=follower)
        c = Client()
        response = c.get("/user_profile/user.id")
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_follower"])

# API Route tests
    def test_valid_like_increment(self):
        user = User.objects.get(username="Alice")
        post = Posts.objects.get(content="Third post of Dan Bilan")
        c = Client()
        response = c.post(f"/likes_update/{post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["likes_count"], 1)

    def test_invalid_like_increment(self):
        user = User.objects.get(username="DanBilan")
        post = Posts.objects.get(content="Forth post of Dan Bilan")
        c = Client()
        response = c.post(f"/likes_update/{post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["likes_count"], 0)

    def test_invalid_post_update(self):
        max_id = Posts.objects.all().aggregate(Max("id"))["id__max"]
        c = Client()
        response = c.get(f"/post_update/{max_id + 1}")
        self.assertEqual(response.status_code, 404)
