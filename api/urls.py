from django.urls import path, include
from .views import analytics_view
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EWasteItemViewSet, CollectionRequestViewSet  # Correct imports

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'ewaste-items', EWasteItemViewSet)
router.register(r'collection-requests', CollectionRequestViewSet, basename='collectionrequest')  # Fixed registration

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', analytics_view, name='analytics'),
]
