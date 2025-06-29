from rest_framework import viewsets, permissions
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    Only authenticated users can create listings.
    All users can view listings.
    """
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Return all listings. You can customize this to filter by location or host.
        """
        return Listing.objects.all()

    def perform_create(self, serializer):
        """
        Automatically assign the current user as the host.
        """
        serializer.save(host=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    Users can only view or create their own bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Limit bookings to the current authenticated user.
        """
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign the booking to the current user.
        """
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """
    Initiates a payment with Chapa for a given booking.
    """
    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found or unauthorized"}, status=404)

    amount = booking.total_price()
    tx_ref = f"booking_{booking.id}_{booking.user.id}"
    email = booking.user.email

    # Setup Chapa payload
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": booking.user.first_name,
        "last_name": booking.user.last_name,
        "tx_ref": tx_ref,
        "callback_url": "https://yourdomain.com/api/payment/verify/",
        "return_url": "https://yourdomain.com/payment-success/",
        "customization": {
            "title": "ALX Travel App Payment",
            "description": f"Payment for booking {booking.id}"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    chapa_url = "https://api.chapa.co/v1/transaction/initialize"
    response = requests.post(chapa_url, json=payload, headers=headers)
    res_data = response.json()

    if res_data.get("status") == "success":
        Payment.objects.create(
            booking=booking,
            amount=amount,
            transaction_id=tx_ref,
            status="pending"
        )
        return Response({
            "checkout_url": res_data["data"]["checkout_url"],
            "tx_ref": tx_ref
        }, status=200)
    return Response({"error": "Payment initiation failed"}, status=400)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Webhook or unauthenticated users may access
def verify_payment(request):
    """
    Verifies the payment status with Chapa and updates the Payment model.
    """
    tx_ref = request.GET.get("tx_ref")
    if not tx_ref:
        return Response({"error": "Missing tx_ref"}, status=400)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    chapa_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    response = requests.get(chapa_url, headers=headers)
    res_data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found"}, status=404)

    if res_data.get("status") == "success":
        payment.status = "completed"
        payment.save()
        return Response({"message": "Payment successful!"})
    else:
        payment.status = "failed"
        payment.save()
        return Response({"message": "Payment failed"}, status=400)
