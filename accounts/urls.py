from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    # -------------------------------
    # User Registration
    # -------------------------------
    path('register/', views.register, name='register'),

    # -------------------------------
    # User Login
    # -------------------------------
    path('login/', CustomLoginView.as_view(), name='login'),

    # -------------------------------
    # User Logout
    # -------------------------------
    path('logout/', views.logout_view, name='logout'),

    # -------------------------------
    # Profile Management
    # -------------------------------
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('provider_availability/', views.provider_availability, name='provider_availability'),
    path('provider_availability/delete/<int:availability_id>/', views.delete_availability, name='delete_availability'),
]
