from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.models import Notification, Job, Service
from accounts.models import Profile
from django.templatetags.static import static


def get_available_timeslots(request):
    provider_id = request.GET.get('provider_id')
    date_str = request.GET.get('date')
    if not provider_id or not date_str:
        return JsonResponse({"error": "Missing provider_id or date"}, status=400)
    
    provider = get_object_or_404(Profile, id=provider_id)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
    
    day_name = date_obj.strftime("%A")
    availability = provider.availabilities.filter(day_of_week=day_name).first()
    if not availability:
        return JsonResponse([], safe=False)
    
    tz = timezone.get_current_timezone()
    avail_start = timezone.make_aware(datetime.combine(date_obj, availability.start_time), tz)
    avail_end = timezone.make_aware(datetime.combine(date_obj, availability.end_time), tz)
    
    booking_duration = timedelta(hours=1)
    increment = timedelta(minutes=15)
    
    candidate_slots = []
    t = avail_start
    now = timezone.now()
    while t + booking_duration <= avail_end:
        if date_obj == now.date() and t < now:
            t += increment
            continue
        candidate_slots.append(t)
        t += increment

    jobs = Job.objects.filter(
        provider=provider,
        scheduled_date__date=date_obj,
        status=Job.IN_PROGRESS
    )
    
    available_slots = []
    for slot in candidate_slots:
        candidate_end = slot + booking_duration
        conflict = False
        for job in jobs:
            job_duration = job.duration if job.duration else timedelta(hours=1)
            job_start = job.scheduled_date
            job_end = job.scheduled_date + job_duration
            if slot < job_end and job_start < candidate_end:
                conflict = True
                break
        if not conflict:
            available_slots.append(slot.isoformat())
    
    return JsonResponse(available_slots, safe=False)

@login_required
def api_unread_notifications(request):
    notifications = request.user.profile.notifications.filter(is_read=False)
    unread_count = notifications.count()
    unread_list = [{
         'id': n.id,
         'message': n.message,
         'link': n.link or '#',
         'created_at': timezone.localtime(n.created_at).strftime("%b %d, %Y, %I:%M %p"),
         'sender_profile_image': n.sender.profile_image.url if n.sender and n.sender.profile_image else static('core/images/default_profile.png')
    } for n in notifications]
    return JsonResponse({'unread_count': unread_count, 'unread_list': unread_list})

@require_POST
@login_required
def api_mark_notification_read(request, notification_id):
    try:
        n = Notification.objects.get(id=notification_id, user=request.user.profile)
        n.is_read = True
        n.save()
        return JsonResponse({'status': 'ok'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@require_POST
@login_required
def api_clear_notifications(request):
    request.user.profile.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

@login_required
def dashboard_counts(request):
    profile = request.user.profile
    pending_bookings = Job.objects.filter(provider=profile, status=Job.PENDING_CONFIRMATION).count()
    services_count = Service.objects.filter(provider=profile).count()
    active_jobs = Job.objects.filter(provider=profile, status=Job.IN_PROGRESS).count()
    return JsonResponse({
        'pending_bookings': pending_bookings,
        'services': services_count,
        'active_jobs': active_jobs,
    })
