from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('superuser/', admin.site.urls),
    path('dashboard/', include('core.dashboard_urls', namespace='dashboard')),
    # path('password-reset/', include('password_reset.urls', namespace='password-reset')),
    path('', include('core.urls', namespace='core')),
]
