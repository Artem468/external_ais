from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Создаёт суперпользователя, если его ещё нет"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "root")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "toor")

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f"Создаю суперпользователя {username}...")
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        else:
            self.stdout.write(f"Суперпользователь {username} уже существует.")
