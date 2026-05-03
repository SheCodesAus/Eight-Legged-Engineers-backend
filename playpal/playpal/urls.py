"""
URL configuration for playpal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# imports Django REST framework that makes URLs for the API
from rest_framework.routers import DefaultRouter
# Imports the VenueView so the router knows where to send the API requests
from venues.views import VenueView
from kids.views import KidView

# Creates multiple API end points so we do have to create lots of unique URL patterns
router = DefaultRouter()
# This creates the details, unique etc - no need to add into the venues
router.register(r'venues', VenueView)
router.register(r'kids', KidView)

urlpatterns = [
    # Directs through to the admin portal.
    path('admin/', admin.site.urls),
    # this is for the api
    path('api/', include(router.urls)),
]
