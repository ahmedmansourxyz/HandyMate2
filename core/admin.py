from django.contrib import admin
from .models import Service, Job, ChatMessage, Review

class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'provider',
        'get_category_display', 
        'task',            
        'price_rate',
        'is_available',
        'created_at'
    )
    list_filter = ('category', 'task', 'is_available', 'created_at')
    search_fields = ('provider__user__username', 'description')
admin.site.register(Service, ServiceAdmin)
admin.site.register(Job)
admin.site.register(ChatMessage)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'client', 'provider', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__user__username', 'provider__user__username', 'job__title')


admin.site.register(Review, ReviewAdmin)
