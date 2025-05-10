from django.contrib import admin 
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    # -------------------------------
    # Admin URLs
    # -------------------------------
    path('admin/', admin.site.urls),
    
    # -------------------------------
    # Accounts App URLs
    # -------------------------------
    path('accounts/', include('accounts.urls')),
    
    # -------------------------------
    # Core App URLs (home, dashboard, services, jobs, etc.)
    # -------------------------------
    path('', include('core.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
