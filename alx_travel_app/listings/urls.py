from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, initiate_payment, verify_payment  # ⬅️ NEW

# DRF router automatically generates URL patterns for viewsets.
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # Include router-generated endpoints (e.g., /listings/, /bookings/)
    path('', include(router.urls)),

    # Payment endpoints
    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/verify/', verify_payment, name='verify_payment'),
]
