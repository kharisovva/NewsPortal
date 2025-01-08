from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import PostForm
from .models import Post
from .filters import NewsFilter

class NewsList(ListView):
    model = Post
    ordering = '-datetime'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'newsone.html'
    context_object_name = 'one_news'


class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_articles')

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == reverse('news_create'):
            post.content_type = 'NE'
        post.save()
        return super().form_valid(form)


class PostEdit(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_articles')


class PostDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_articles')
