from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from .views import ProductViewSet

router.register(r"product", ProductViewSet)

from .views import ProductCategoryViewSet

router.register(r"productcategory", ProductCategoryViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include generated URLs for Inventory
]
    