from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post

class NewsList(ListView):
    model = Post
    ordering = '-datetime'
    template_name = 'news.html'
    context_object_name = 'news'


class NewsDetail(DetailView):
    model = Post
    template_name = 'newsone.html'
    context_object_name = 'one_news'