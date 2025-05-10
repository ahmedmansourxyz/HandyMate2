from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse
from django.db.models import Min
import json
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince
from core.models import Job, Notification, Service, Review
from core.forms import ChatMessageForm, ServiceAddForm, JobDurationUpdateForm, ReviewForm
from accounts.models import Profile
from core.constants import SERVICE_CATEGORIES, TASKS_BY_CATEGORY, CATEGORY_IMAGES


def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    if request.user.profile.is_provider:
        return redirect('provider_dashboard')
    profile = request.user.profile
    jobs = Job.objects.filter(client=profile)
    total_jobs = jobs.count()
    active_jobs = jobs.exclude(status='COMPLETED')
    pending_jobs = jobs.filter(status='PENDING_CONFIRMATION').count()
    canceled_jobs = jobs.filter(status='CANCELLED').count()
    notification_count = profile.notifications.filter(is_read=False).count()
    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'jobs': jobs,
        'total_jobs': total_jobs,
        'pending_jobs': pending_jobs,
        'active_jobs': active_jobs.count(),
        'canceled_jobs': canceled_jobs,
        'notification_count': notification_count,
    })

@login_required
def provider_dashboard(request):
    if not request.user.profile.is_provider:
        return redirect('dashboard')
    provider = request.user.profile
    services = Service.objects.filter(provider=provider)
    pending_jobs = Job.objects.filter(provider=provider, status=Job.PENDING_CONFIRMATION)
    active_jobs = Job.objects.filter(provider=provider, status=Job.IN_PROGRESS)
    
    pending_bookings = []
    for job in pending_jobs:
        earnings = job.price_rate_snapshot
        if earnings is None:
            matching_service = None
            for s in services.filter(category__iexact=job.category):
                if s.full_task_display.lower() == (job.task or "").lower():
                    matching_service = s
                    break
            if matching_service:
                earnings = matching_service.price_rate
        pending_bookings.append({
            'job': job,
            'earnings': earnings,
        })

    return render(request, 'core/provider_dashboard.html', {
        'services': services,
        'pending_bookings': pending_bookings,
        'active_jobs': active_jobs,
    })

@login_required
def provider_jobs(request, provider_id):
    provider = get_object_or_404(Profile, id=provider_id, is_provider=True)
    jobs = Job.objects.filter(provider=provider).order_by('-created_at')
    return render(request, 'core/provider_jobs.html', {'jobs': jobs, 'provider': provider})

@login_required
def add_service(request):
    if not request.user.profile.is_provider:
        messages.error(request, "Only service providers can add services.")
        return redirect('provider_dashboard')
    
    provider = request.user.profile
    current_step = 1  
    if request.method == 'POST':
        form = ServiceAddForm(request.POST, provider=provider)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = provider
            service.save()
            messages.success(request, "Service added successfully.")
            return redirect(f"{reverse('provider_dashboard')}?new_service_id={service.id}")
        else:
            error_message = " ".join([" ".join(errors) for field, errors in form.errors.items()])
            messages.error(request, error_message)
            if "already added" in error_message.lower():
                current_step = 1
                form = ServiceAddForm(provider=provider)
            else:
                current_step = 3
                form = ServiceAddForm(initial={
                    'category': request.POST.get('category'),
                    'task': request.POST.get('task'),
                    'price_rate': request.POST.get('price_rate'),
                }, provider=provider)
    else:
        form = ServiceAddForm(provider=provider)
    
    context = {
        'form': form,
        'service_categories': SERVICE_CATEGORIES,
        'tasks_by_category': TASKS_BY_CATEGORY,
        'category_images': CATEGORY_IMAGES,
        'current_step': current_step,
    }
    return render(request, 'core/add_service.html', context)


def services_overview(request):
    category_cards = []
    for cat_key, cat_label in SERVICE_CATEGORIES:
        # Use the hard-coded path from CATEGORY_IMAGES
        image_url = CATEGORY_IMAGES.get(cat_key)
        card = {
            'key': cat_key,
            'label': cat_label,
            'image': image_url,
            'tasks': []
        }
        tasks = TASKS_BY_CATEGORY.get(cat_key, [])
        for task in tasks:
            task_value, task_label = task
            min_price_data = Service.objects.filter(
                category=cat_key, 
                task=task_value,
                is_available=True
            ).aggregate(min_price=Min('price_rate'))
            min_price = min_price_data['min_price']
            card['tasks'].append({
                'value': task_value,
                'label': task_label,
                'min_price': min_price,
            })
        category_cards.append(card)
    context = {'category_cards': category_cards}
    return render(request, 'core/services_overview.html', context)


def service_providers(request, category, task):
    category_dict = dict(SERVICE_CATEGORIES)
    category_label = category_dict.get(category, category)
    
    if task.lower() == "all":
        providers = Profile.objects.filter(
            is_provider=True,
            service__category=category,
            service__is_available=True
        ).distinct()
        context = {
            "providers": providers,
            "service_category": category_label,
            "task": "all",
        }
    else:
        services = Service.objects.filter(
            category=category,
            task=task,
            is_available=True
        )
        providers = Profile.objects.filter(
            is_provider=True,
            service__in=services
        ).distinct()
        context = {
            "providers": providers,
            "service_category": category_label,
            "task": task,
        }
    return render(request, "core/service_providers.html", context)


@login_required
def list_providers(request, category):
    task = request.GET.get('task')
    providers = Profile.objects.filter(is_provider=True, service__category=category).distinct()
    
    if task:
        providers = providers.filter(service__task=task)
    
    min_experience = request.GET.get('min_experience')
    location = request.GET.get('location')
    is_available = request.GET.get('is_available')

    if min_experience:
        providers = providers.filter(years_of_experience__gte=min_experience)
    if location:
        providers = providers.filter(city__icontains=location)
    if is_available == 'true':
        providers = providers.filter(is_available=True)

    context = {
        'providers': providers,
        'category': category,
        'selected_task': task,
        'min_experience': min_experience,
        'location': location,
        'is_available': is_available,
        'tasks': TASKS_BY_CATEGORY,  
    }
    return render(request, 'core/list_providers.html', context)

@login_required
def provider_jobs(request):
    if not request.user.profile.is_provider:
        messages.error(request, "Only service providers can view their jobs.")
        return redirect('dashboard')
    jobs = Job.objects.filter(provider=request.user.profile).order_by('-created_at')
    return render(request, 'core/provider_jobs.html', {'jobs': jobs})


@login_required
@require_POST
def ajax_update_job_duration(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.provider != request.user.profile:
        return JsonResponse({'error': "Permission denied"}, status=403)
    
    try:
        data = json.loads(request.body)
        new_duration = data.get('duration')
    except Exception:
        return JsonResponse({'error': "Invalid data"}, status=400)
    
    form = JobDurationUpdateForm({'duration': new_duration}, instance=job)
    if form.is_valid():
        form.save()
        Notification.objects.create(
            user=job.client,
            sender=job.provider,
            message=f"The duration for your job '{job.task}' has been updated to {job.duration}.",
            link=reverse('job_detail', args=[job.id])
        )
        return JsonResponse({
            'success': True,
            'message': "Job duration updated successfully.",
            'new_duration': str(job.duration)
        })
    else:
        errors = form.errors.as_json()
        return JsonResponse({'error': "Invalid input", 'errors': errors}, status=400)

@login_required
def accept_booking(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    # Only the assigned provider can accept the booking
    if job.provider != request.user.profile:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            messages.error(request, "Permission denied.")
            return HttpResponseRedirect(reverse('my_jobs'))
    
    # If the job is cancelled, do not allow acceptance
    if job.status == 'CANCELLED':
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'error': "This booking has been cancelled by the client."}, status=400)
        else:
            messages.error(request, "This booking has been cancelled by the client.")
            return HttpResponseRedirect(reverse('my_jobs'))
    
    # Ensure that the job is in a state that can be accepted (only pending confirmation)
    if job.status != Job.PENDING_CONFIRMATION:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'error': "Booking cannot be accepted in its current status."}, status=400)
        else:
            messages.error(request, "Booking cannot be accepted in its current status.")
            return HttpResponseRedirect(reverse('my_jobs'))
    
    job.status = Job.IN_PROGRESS
    job.save()
    Notification.objects.create(
        user=job.client,
        sender=job.provider,
        message=f"Your booking for '{job.task}' has been accepted!",
        link=reverse('job_detail', args=[job.id])
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        job_data = {
            'id': job.id,
            'task': job.task,
            'category': job.category,
            'duration': str(job.duration),
            'client_username': job.client.user.username,
            'client_profile_image': job.client.profile_image.url if job.client.profile_image else static('core/images/default_profile.png'),
            'formatted_created': f"{timesince(job.created_at)} ago",
            'formatted_scheduled': job.scheduled_date.strftime("%b %d, %Y, %H:%M") if job.scheduled_date else 'Not scheduled',
            'client_email': job.client.user.email,
            'client_phone': job.client.phone_number,
            'client_address': job.client.address,
            'client_city': job.client.city,
        }
        return JsonResponse({
            'success': True,
            'message': "Booking accepted successfully.",
            'level': 'success',
            'job': job_data
        })
    else:
        messages.success(request, "Booking accepted successfully.")
        return HttpResponseRedirect(reverse('my_jobs'))

@login_required
def decline_booking(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if job.provider != request.user.profile:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            messages.error(request, "Permission denied.")
            return HttpResponseRedirect(reverse('my_jobs'))
            
    Notification.objects.create(
        user=job.client,
        sender=job.provider,
        message=f"Your booking for '{job.task}' has been declined.",
    )
    job.delete()
    
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({'success': True, 'message': "Booking declined.", 'level': 'info'})
    else:
        messages.info(request, "Booking declined.")
        return HttpResponseRedirect(reverse('my_jobs'))

def my_jobs(request):
    if request.user.profile.is_provider:
        jobs = Job.objects.filter(provider=request.user.profile).order_by('-created_at')
    else:
        jobs = Job.objects.filter(client=request.user.profile).order_by('-created_at')
    return render(request, 'core/my_jobs.html', {'jobs': jobs})

def job_detail(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        messages.error(request, "The job you are trying to view no longer exists.")
        return redirect('dashboard')
    
    review_form = None
    if (not request.user.profile.is_provider and job.status == Job.COMPLETED 
        and not hasattr(job, 'review')):
        review_form = ReviewForm()
    
    context = {
        'job': job,
        'review_form': review_form,
    }
    return render(request, 'core/job_detail.html', context)

@login_required
def job_chat(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    messages_list = job.chat_messages.all().order_by('timestamp')
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_msg = form.save(commit=False)
            chat_msg.job = job
            chat_msg.sender = request.user.profile
            chat_msg.save()
            
            if chat_msg.sender == job.client and job.provider:
                receiver = job.provider
            elif chat_msg.sender == job.provider:
                receiver = job.client
            else:
                receiver = None
            
            if receiver:
                Notification.objects.create(
                    user=receiver,
                    sender=chat_msg.sender,
                    message=f"You have a new message in the chat for job '{job.task}'.",
                    link=reverse('job_chat', args=[job.id])
                )
            
            return redirect('job_chat', job_id=job.id)
    else:
        form = ChatMessageForm()
    context = {'job': job, 'messages_list': messages_list, 'form': form}
    return render(request, 'core/job_chat.html', context)

@login_required
def toggle_service_availability(request, service_id):
    try:
        service = Service.objects.get(id=service_id, provider=request.user.profile)
    except Service.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'error': "Service not found or you don't have permission."}, status=404)
        else:
            messages.error(request, "Service not found or you don't have permission.")
            return redirect('provider_dashboard')
    
    service.is_available = not service.is_available
    service.save()
    state = "enabled" if service.is_available else "disabled"
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({'success': True, 'message': f"Service {state} successfully.", 'new_state': service.is_available})
    else:
        messages.success(request, f"Service {state} successfully.")
        return redirect('provider_dashboard')
    
@require_POST
@login_required
def ajax_update_service_price(request, service_id):
    try:
        service = Service.objects.get(id=service_id, provider=request.user.profile)
    except Service.DoesNotExist:
        return JsonResponse({'error': "Service not found or you don't have permission."}, status=404)
    
    new_price = request.POST.get('price_rate')
    if new_price:
        try:
            new_price = float(new_price)
            if new_price < 0:
                return JsonResponse({'error': "Price must be a positive number."}, status=400)
        except ValueError:
            return JsonResponse({'error': "Invalid price."}, status=400)
        service.price_rate = new_price
        service.save()
        return JsonResponse({'success': True, 'new_price': f"{service.price_rate:.2f}", 'message': "Service price updated successfully.", 'level': 'success'})
    else:
        return JsonResponse({'error': "Price rate is required."}, status=400)

@require_POST
@login_required
def ajax_delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id, provider=request.user.profile)
    except Service.DoesNotExist:
        return JsonResponse({'error': "Service not found or you don't have permission."}, status=404)
    service.delete()
    return JsonResponse({'success': True, 'message': "Service deleted successfully.", 'level': 'success'})

@login_required
def notifications(request):
    # Retrieves all notifications for the logged in user's profile ordered by newest first.
    notifications = request.user.profile.notifications.all().order_by('-created_at')
    return render(request, 'core/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user.profile)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user.profile)
    notification.delete()
    return redirect('notifications')

@login_required
def list_services(request):
    category = request.GET.get('category')
    task = request.GET.get('task')
    max_price = request.GET.get('max_price')
    location = request.GET.get('location')
    sort_by = request.GET.get('sort_by')
    
    services = Service.objects.all()
    if category:
        services = services.filter(category=category)
    if task:
        services = services.filter(task=task)
    if max_price:
        services = services.filter(price_rate__lte=max_price)
    if location:
        services = services.filter(provider__city__icontains=location)
    
    if sort_by == 'cheapest':
        services = services.order_by('price_rate')
    elif sort_by == 'most_experienced':
        services = services.order_by('-provider__years_of_experience')
    
    context = {
        'services': services,
        'categories': SERVICE_CATEGORIES,
        'tasks': TASKS_BY_CATEGORY,
        'selected_category': category,
        'selected_task': task,
        'max_price': max_price,
        'location': location,
    }
    return render(request, 'core/list_services.html', context)

@login_required
def cancel_job(request, job_id):
    # Retrieve the job without filtering by client only.
    job = get_object_or_404(Job, id=job_id)
    user_profile = request.user.profile

    # Check if the current user is either the client or the provider.
    if user_profile != job.client and user_profile != job.provider:
        messages.error(request, "You don't have permission to cancel this job.")
        return redirect('my_jobs')

    # You can decide which job statuses are eligible for cancellation.
    if job.status not in [Job.PENDING_CONFIRMATION, Job.IN_PROGRESS]:
        messages.error(request, "This job cannot be cancelled at this stage.")
        return redirect('my_jobs')

    # Update the job status to 'CANCELLED'
    job.status = 'CANCELLED'
    job.save()

    # Send a notification to the other party.
    if user_profile == job.client and job.provider:
        # Client cancelled: notify provider.
        Notification.objects.create(
            user=job.provider,
            sender=job.client,
            message=f"Your booking for '{job.task}' has been cancelled by the client."
        )
    elif user_profile == job.provider:
        # Provider cancelled: notify client.
        Notification.objects.create(
            user=job.client,
            sender=job.provider,
            message=f"Your booking for '{job.task}' has been cancelled by the service provider."
        )

    messages.success(request, "Job has been cancelled successfully.")
    return redirect('my_jobs')

@login_required
def add_review(request, job_id):
    # Ensure only the client who created the job can review and that job is completed.
    job = get_object_or_404(Job, id=job_id, client=request.user.profile, status=Job.COMPLETED)
    
    # If a review already exists, do not allow another
    if hasattr(job, 'review'):
        messages.error(request, "You have already reviewed this job.")
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.job = job
            review.client = request.user.profile
            review.provider = job.provider
            review.save()
            
            # Update the provider's overall rating based on all received reviews.
            Review.update_provider_rating(job.provider)
            
            # Create a notification for the provider that a new review has been submitted.
            Notification.objects.create(
                user=job.provider,
                sender=job.client,
                message=f"You received a new review for job '{job.task}'.",
                link=reverse('job_detail', args=[job.id])
            )
            
            messages.success(request, "Thank you for your review!")
            return redirect('job_detail', job_id=job_id)
    else:
        form = ReviewForm()
    
    return render(request, 'core/add_review.html', {'form': form, 'job': job})

@login_required
def complete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.client != request.user.profile:
        messages.error(request, "You don't have permission to complete this job.")
        return redirect('job_detail', job_id=job_id)
    if job.status != Job.IN_PROGRESS:
        messages.error(request, "Only jobs in progress can be marked as completed.")
        return redirect('job_detail', job_id=job_id)
    
    job.status = Job.COMPLETED
    job.completed_date = timezone.now()
    job.save()
    
    if job.provider:
        # Increment the provider's completed jobs count
        job.provider.completed_jobs += 1
        job.provider.save()
        
        Notification.objects.create(
            user=job.provider,
            sender=job.client,
            message=f"The job '{job.task}' has been marked as completed by the client.",
            link=reverse('job_detail', args=[job.id])
        )
    
    messages.success(request, "Job marked as completed!")
    return redirect('job_detail', job_id=job_id)


@login_required
def provider_details_modal(request, provider_id):
    provider = get_object_or_404(Profile, id=provider_id, is_provider=True)
    html = render_to_string('core/provider_modal.html', {'provider': provider}, request=request)
    return HttpResponse(html)
