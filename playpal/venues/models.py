from django.db import models
from django.conf import settings

class Venue(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ('Activity', 'Activity'),
        ('Eatery', 'Eatery'),
    ]
    
    main_category = models.CharField(max_length=20, choices=MAIN_CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100)
    opening_times = models.CharField(max_length=255, blank=True)
    age_range = models.CharField(max_length=20, blank=True)
    cost = models.CharField(max_length=20, blank=True)
    kids_eat_free = models.CharField(max_length=50, blank=True)
    indoor_outdoor = models.CharField(max_length=20, blank=True)
    wheelchair_friendly = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image_url = models.URLField(max_length=500, blank=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_venues'
    )
    
    verify_before_launch = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['main_category', 'sub_category']),
            models.Index(fields=['suburb']),
        ]
    
    def __str__(self):
        return f"{self.sub_category} - {self.suburb}"