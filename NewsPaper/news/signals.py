from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import mail_managers, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from .models import Post, PostCategory


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
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
                        {
                            'post': instance,
                            'post_url': f"http://127.0.0.1:8000//news/{instance.id}"
                         }
                    )
                    post_heading = instance.heading
                    msg = EmailMultiAlternatives(
                        subject=f"Новая статья: {post_heading}",
                        body=f'Здравствуй! Новая статья в твоем любимом разделе!\n{instance.content[:50]}',
                        from_email='kharisovak@yandex.ru',
                        to=[subscriber.email]
                    )
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send()