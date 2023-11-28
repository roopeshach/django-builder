from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from .views import WaiterViewSet

router.register(r"waiter", WaiterViewSet)

from .views import CookViewSet

router.register(r"cook", CookViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include generated URLs for Restaurant
]
    