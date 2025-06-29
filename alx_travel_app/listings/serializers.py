from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model.
    The 'host' and 'created_at' fields are read-only.
    """
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['host', 'created_at']

    def create(self, validated_data):
        """
        Ensure the logged-in user is set as the host automatically.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['host'] = request.user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    Adds a read-only 'total_price' field calculated from model logic.
    """
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'total_price']

    def get_total_price(self, obj):
        """
        Calculate total price using the model method.
        """
        return obj.total_price()

    def create(self, validated_data):
        """
        Automatically assign the booking user as the logged-in user.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
