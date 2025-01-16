from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives

from .forms import PostForm
from .models import Post, Author
from .filters import NewsFilter


class NewsList(LoginRequiredMixin, ListView):
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
        context['is_not_author'] = not self.request.user.groups.filter(name='author').exists()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'newsone.html'
    context_object_name = 'one_news'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_articles')

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == reverse('news_create'):
            post.content_type = 'NE'
        post.save()

        html_content = render_to_string(
            'post_created.html',
            {'post': post}
        )
        msg = EmailMultiAlternatives(
            subject=Post.heading,
            body=f'Здравствуй! Новая статья в твоем любимом разделе!\n{post.content[:50]}',
            from_email='kharisovak@yandex.ru',
            to=['harisova_k@mail.ru']
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return super().form_valid(form)


class PostEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_articles')


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_articles')


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='author')
    if not request.user.groups.filter(name='author').exists():
        author_group.user_set.add(user)
    return redirect('/news/')
