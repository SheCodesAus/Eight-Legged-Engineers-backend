from django.db import models
from django.conf import settings

class Venue(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ('Activity', 'Activity'),
        ('Eatery', 'Places to Eat'),
    ]
    
    main_category = models.CharField(max_length=20, choices=MAIN_CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=50)
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100)
    opening_times = models.CharField(max_length=255, blank=True)
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
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
    
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    ratings_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['main_category', 'sub_category']),
            models.Index(fields=['suburb']),
            models.Index(fields=['is_published']),
        ]
    
    # when a venue is soft deleted, the corresponding ratings are also soft deleted.
    def save(self, *args, **kwargs):
        if self.is_archived:
            self.ratings.update(is_archived=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"{self.sub_category} - {self.suburb}"


class Rating(models.Model):
    RATING_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    rating_type = models.CharField(max_length=3, choices=RATING_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ratings'
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} rated {self.venue} - {self.rating_type}"