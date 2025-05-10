from django.contrib import admin
from .models import Profile, ProviderAvailability

class ProviderAvailabilityInline(admin.TabularInline):
    model = ProviderAvailability
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProviderAvailabilityInline]
    list_display = ('user', 'city', 'years_of_experience', 'is_provider')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProviderAvailability)