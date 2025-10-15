from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, InventoryChangeViewSet, CategoryViewSet

app_name = 'store'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'inventory-changes', InventoryChangeViewSet, basename='inventory-change')

urlpatterns = [
    path('api/', include(router.urls)),
]
