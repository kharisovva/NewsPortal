from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_managers, EmailMultiAlternatives
from django.template.loader import render_to_string

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