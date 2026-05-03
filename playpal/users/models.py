from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

# Month choices 1-12 (display as 01..12)
MONTH_CHOICES = [(i, f"{i:02d}") for i in range(1, 13)]


class CustomUsers(AbstractUser):
    # Matches the Supabase user ID so Django can link requests back to the right account.
    supabase_uid = models.CharField(max_length=255, unique=True)

    # The user's display name in the app.
    first_name = models.CharField(max_length=150, blank=True)

    # Email is the main identity used by Supabase authentication.
    email = models.EmailField(unique=True)

    # Django keeps this field for compatibility, but Supabase handles real sign-in.
    password = models.CharField(max_length=128, blank=True)

    # App-level admin flag.
    is_superuser = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('!'):
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username
    
class Kids(models.Model):
    # Month of birth (1-12) — limited to explicit choices for UI/forms
    birth_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    # Year of birth (four digits preferable). Must be no earlier than 2010.
    birth_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2010)]
    )
    # Link to the CustomUser profile created by Supabase authentication
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kids'
    )
    
    # Rely on field validators for birth_year (no DB-level CheckConstraint)

    