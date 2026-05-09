from django.db import models

class Suburb(models.Model):
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=10)
    postcode = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.suburb}, {self.state} {self.postcode}"