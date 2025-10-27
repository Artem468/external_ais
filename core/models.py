from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    params = models.JSONField(default=dict, verbose_name="Параметры")
    max_daily_requests = models.IntegerField(null=True, blank=True, verbose_name="Максимальное количество заявок")

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["username"]
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Request(models.Model):
    STATUS_CHOICES = [
        ("processed", "На рассмотрение"),
        ("await", "Доработка"),
        ("accept", "Завершена"),
        ("reject", "Отказано"),
    ]

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    params = models.JSONField(default=dict, verbose_name="Параметры")
    text = models.TextField(null=True, blank=True, verbose_name="Описание")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="processed", verbose_name="Статус", null=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return f"#{self.id} | {self.get_status_display()}"

    class Meta:
        db_table = "request"
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"