from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

MONTH_CHOICES = [(i, f"{i:02d}") for i in range(1, 13)]


class CustomUser(AbstractUser):
    supabase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.email or self.username


class Kids(models.Model):
    birth_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    birth_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2010)]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kids'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kid born {self.birth_month}/{self.birth_year}"
