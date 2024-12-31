from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = 0
        comments_rating = 0
        posts_comments_rating = 0

        posts = Post.objects.filter(author=self)
        for p in posts:
            posts_rating += p.rating

        comments = Comment.objects.filter(user=self.author)
        for c in comments:
            comments_rating += c.rating

        posts_comments = Comment.objects.filter(post__author=self)
        for pc in posts_comments:
            posts_comments_rating += pc.rating

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Post(models.Model):
    article = 'AR'
    news = 'NE'
    POSTS = [
        (article, 'статья'),
        (news, 'новость')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through='PostCategory')
    content_type = models.CharField(max_length=2,
                                    choices=POSTS,
                                    default=article)
    datetime = models.DateTimeField(auto_now_add=True)
    heading = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        preview_text = self.content[:125] + "..." if len(self.content) > 125 else self.content
        return preview_text


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
