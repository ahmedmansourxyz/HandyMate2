from django.db import models
from accounts.models import Profile
from core.constants import SERVICE_CATEGORIES
from datetime import timedelta
from django.db.models import Avg


class Service(models.Model):
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=100,
        choices=SERVICE_CATEGORIES
    )
    task = models.CharField(max_length=100)
    price_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_task_display(self):
        from core.constants import TASKS_BY_CATEGORY
        normalized_category = self.category
        for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
            if code == self.task:
                return label
        return self.task
    
    class Meta:
        unique_together = ('provider', 'category', 'task')
    def __str__(self):
        return f"{self.full_task_display} ({self.provider.user.username})"


class Job(models.Model):
    PENDING_CONFIRMATION = 'PENDING_CONFIRMATION'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    
    STATUS_CHOICES = [
        (PENDING_CONFIRMATION, 'Pending Confirmation'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]
    
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='client_jobs')
    task = models.CharField(max_length=200)
    note = models.TextField(verbose_name="Note")
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=PENDING_CONFIRMATION)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default=timedelta(hours=1))
    provider = models.ForeignKey('accounts.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='provider_jobs')
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    price_rate_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        if self.provider:
            return f"{self.task} - {self.provider.user.username}"
        return f"{self.task} - {self.client.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.user.username}"


class ChatMessage(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.user.username} on {self.job.task}"

class Review(models.Model):
    job = models.OneToOneField('Job', on_delete=models.CASCADE, related_name="review")
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_given')
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.provider.user.username} ({self.rating}/5)"

    @staticmethod
    def update_provider_rating(provider):
        avg = provider.reviews_received.aggregate(Avg('rating'))['rating__avg']
        provider.rating = round(avg, 1) if avg else 0
        provider.save()