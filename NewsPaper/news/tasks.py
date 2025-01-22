from datetime import timedelta

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

from NewsPaper.news.models import Category, Post


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