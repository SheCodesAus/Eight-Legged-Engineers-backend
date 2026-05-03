from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Kid(models.Model):
    birth_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(9999)]
    )
    birth_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kids'
    )

    def __str__(self):
        return f"Kid of {self.user} ({self.birth_month}/{self.birth_year})"
