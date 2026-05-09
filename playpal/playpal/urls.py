from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Directs through to the admin portal.
    path('admin/', admin.site.urls),
    # venues endpoints (defined in venues/urls.py)
    path('api/', include('venues.urls')),
    # suburbs autocomplete API (defined in suburbs/urls.py)
    path('api/suburbs/', include('suburbs.urls')),
]