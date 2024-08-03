from django.db import models
from django.contrib import admin

class AmoAcc(models.Model):
    name = models.CharField(max_length=2000)
    google_link = models.CharField(max_length=1000)
    long_term_token = models.CharField(max_length=2000)
    lead_filter = models.CharField(max_length=1000)
    event_filter = models.CharField(max_length=1000)
    def __str__(self):
        return self.name
    
admin.site.register(AmoAcc)