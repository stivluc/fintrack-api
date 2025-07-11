from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AccountViewSet, AssetViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'assets', AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]