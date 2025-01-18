import logging
from datetime import timedelta

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.timezone import now
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Category, Post

logger = logging.getLogger(__name__)


def weekly_digest():
    #  Your job processing logic here... 
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


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            weekly_digest,
            trigger=CronTrigger(second="*/10"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="weekly_digest",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_digest'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")