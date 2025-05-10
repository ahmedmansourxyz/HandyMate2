from django.urls import path
from . import views, api_views
from .views_booking import BookingWizardWithoutService, BookingWizardWithService

urlpatterns = [
    # -------------------------------
    # Home and Dashboard URLs
    # -------------------------------
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),

    # -------------------------------
    # Service Management URLs
    # (Manage services: add, toggle, update, delete, and list providers/services)
    # -------------------------------
    path('services/<int:service_id>/toggle/', views.toggle_service_availability, name='toggle_service_availability'),
    path('ajax/service/<int:service_id>/update/', views.ajax_update_service_price, name='ajax_update_service_price'),
    path('ajax/service/<int:service_id>/delete/', views.ajax_delete_service, name='ajax_delete_service'),
    path('services/', views.services_overview, name='services_overview'),
    path('services/add-service/', views.add_service, name='add_service'),
    path('services/<str:category>/<str:task>/', views.service_providers, name='service_providers'),
    path('providers/<str:category>/', views.list_providers, name='list_providers'),

    # -------------------------------
    # Job Management URLs
    # (Job details, chat, acceptance/decline, completion, cancellation, updates, and reviews)
    # -------------------------------
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/chat/', views.job_chat, name='job_chat'),
    path('job/<int:job_id>/accept/', views.accept_booking, name='accept_booking'),
    path('job/<int:job_id>/decline/', views.decline_booking, name='decline_booking'),
    path('job/<int:job_id>/complete/', views.complete_job, name='complete_job'),
    path('job/<int:job_id>/cancel/', views.cancel_job, name='cancel_job'),
    path('job/<int:job_id>/update_duration/', views.ajax_update_job_duration, name='ajax_update_job_duration'),
    path('job/<int:job_id>/review/', views.add_review, name='add_review'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('provider-jobs/', views.provider_jobs, name='provider_jobs'),
    path('provider/<int:provider_id>/jobs/', views.provider_jobs, name='provider_jobs'),

    # -------------------------------
    # Booking Wizard URLs
    # (Book a service via a multi-step wizard; one with a preselected service and one without)
    # -------------------------------
    path('book-service/<int:provider_id>/<str:service_category>/',
         BookingWizardWithoutService.as_view(),
         name='book_service_wizard'),
    path('book-service/<int:provider_id>/<str:service_category>/<str:service>/',
         BookingWizardWithService.as_view(),
         name='book_service_wizard_with_service'),

    # -------------------------------
    # API Endpoints
    # (AJAX endpoints for time slots, notifications, and dashboard counts)
    # -------------------------------
    path('api/get-available-timeslots/', api_views.get_available_timeslots, name='get_available_timeslots'),
    path('api/unread_notifications/', api_views.api_unread_notifications, name='api_unread_notifications'),
    path('api/mark_notification_read/<int:notification_id>/', api_views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/clear_notifications/', api_views.api_clear_notifications, name='api_clear_notifications'),
    path('api/dashboard_counts/', api_views.dashboard_counts, name='dashboard_counts'),

    # -------------------------------
    # Provider Detail Modal URL
    # (Load provider details via a modal)
    # -------------------------------
    path('provider/<int:provider_id>/modal/', views.provider_details_modal, name='provider_modal'),
]
