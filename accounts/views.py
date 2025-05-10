from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, ProfileUpdateForm, ProviderAvailabilityForm
from .models import ProviderAvailability


class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_success_url(self):
        if self.request.user.profile.is_provider:
            return reverse('provider_dashboard')
        else:
            return reverse('dashboard')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.is_provider = (form.cleaned_data.get('user_type') == 'provider')
            user.profile.save()
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            if user.profile.is_provider:
                return redirect('provider_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def profile_update(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
    return redirect('profile_view')

def profile_view(request):
    profile = request.user.profile
    update_form = ProfileUpdateForm(instance=profile)
    return render(request, 'core/profile_view.html', {
        'profile': profile,
        'update_form': update_form,
    })

@login_required
def provider_availability(request):
    profile = request.user.profile
    if not profile.is_provider:
        messages.error(request, "Only service providers can access the calendar.")
        return redirect('dashboard')

    availabilities = ProviderAvailability.objects.filter(provider=profile)
    
    if request.method == 'POST':
        form = ProviderAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.provider = profile
            availability.save()
            messages.success(request, "Availability added successfully.")
            return redirect('provider_availability')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = ProviderAvailabilityForm()

    return render(request, 'core/provider_availability.html', {
        'availabilities': availabilities,
        'form': form,
    })

@login_required
def delete_availability(request, availability_id):
    profile = request.user.profile
    availability = get_object_or_404(ProviderAvailability, id=availability_id, provider=profile)
    if request.method == 'POST':
        availability.delete()
        messages.success(request, "Availability deleted successfully.")
    return redirect('provider_availability')
