from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import mail_managers, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from .models import Post


@receiver(post_save, sender=Post)
def notify_about_new_post(sender, instance, created, **kwargs):
    if created:
        # Получаем категории, связанные с созданным постом
        categories = instance.category.all()

        # Для каждой категории отправляем письма подписчикам
        for category in categories:
            # Проверяем подписчиков категории
            subscribers = category.subscribers.all()
            if subscribers.exists():
                for subscriber in subscribers:
                    html_content = render_to_string(
                        'post_created.html',
                        {'post': instance}
                    )
                    post_heading = instance.heading
                    msg = EmailMultiAlternatives(
                        subject=f"Новая статья: {post_heading}",
                        body=f'Здравствуй! Новая статья в твоем любимом разделе!\n{instance.content[:50]}',
                        from_email='kharisovak@yandex.ru',
                        to=[sender.category.subscribers.email]
                    )
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send()


@receiver(pre_save, sender=Post)
def limit_news_per_user(sender, instance, **kwargs):
    # Получаем текущую дату
    today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now().replace(hour=23, minute=59, second=59, microsecond=999999)

    # Считаем количество новостей, опубликованных пользователем за сегодня
    news_count = Post.objects.filter(
        author=instance.author,  # Фильтруем по автору
        datetime__range=(today_start, today_end)  # За текущие сутки
    ).count()

    # Проверяем, превышен ли лимит
    if news_count >= 3:
        raise ValidationError("Вы не можете публиковать более трёх новостей в сутки.")
