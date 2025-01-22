from datetime import timedelta

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

from NewsPaper.news.models import Category, Post


@shared_task
def create_news_celery(pk):
    # Получаем категории, связанные с созданным постом
    post = Post.objects.filter(pk=pk)
    categories = post.category.all()

    # Для каждой категории отправляем письма подписчикам
    for category in categories:
        # Проверяем подписчиков категории
        subscribers = category.subscribers.all()
        if subscribers.exists():
            for subscriber in subscribers:
                html_content = render_to_string(
                    'post_created.html',
                    {
                        'post': post,
                        'post_url': f"http://127.0.0.1:8000//news/{post.id}"
                    }
                )
                post_heading = post.heading
                msg = EmailMultiAlternatives(
                    subject=f"Новая статья: {post_heading}",
                    body=f'Здравствуй! Новая статья в твоем любимом разделе!\n{post.content[:50]}',
                    from_email='kharisovak@yandex.ru',
                    to=[subscriber.email]
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()


@shared_task
def weekly_digest_celery():
    """ Еженедельная отправка новостей в категории подписчикам"""

    # Получаем дату начала и конца прошлой недели
    week_ago = now() - timedelta(days=7)

    # Проходим по всем категориям
    for category in Category.objects.all():
        # Собираем статьи за последние 7 дней для этой категории
        posts = Post.objects.filter(category=category, datetime__gte=week_ago)

        if posts.exists():
            # Формируем список подписчиков этой категории
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                # Генерируем HTML-содержимое письма
                html_content = render_to_string(
                    'weekly_digest.html',
                    {
                        'posts': posts,
                        'subscriber': subscriber,
                        'category': category,
                    }
                )

                # Тема письма
                subject = f"Еженедельная подборка новых статей в категории {category.name}"

                # Формируем текстовое письмо
                text_content = "\n".join(
                    [f"{post.heading}: http://127.0.0.1:8000//news/{post.id}" for post in posts]
                )

                # Отправляем письмо
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email='kharisovak@yandex.ru',
                    to=[subscriber.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()