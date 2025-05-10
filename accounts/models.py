from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_provider = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    completed_jobs = models.PositiveIntegerField(default=0)
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_available = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username

    @property
    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()

class ProviderAvailability(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), #value in db, label
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="Time when the provider starts accepting jobs (e.g., 08:00)")
    end_time = models.TimeField(help_text="Time when the provider stops accepting jobs (e.g., 17:00)")
    
    def __str__(self):
        return f"{self.provider.user.username} - {self.day_of_week}: {self.start_time} to {self.end_time}"
