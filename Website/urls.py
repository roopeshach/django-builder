from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from .views import BlogViewSet

router.register(r"blog", BlogViewSet)

from .views import ServiceViewSet

router.register(r"service", ServiceViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include generated URLs for Website
]
    