from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from rest_framework import serializers
    
from .models import Post, About, Profile, Room, Booking, CheckIn, Place

class CustomLoginSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        adapter = get_adapter()
        user = adapter.authenticate(self.context['request'], username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is not active.")

        return user
    
    # booking 


class RoomSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name')

    class Meta:
        model = Room
        fields = '__all__'

    def create(self, validated_data):
        return super().create(self.category_name)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class CheckinSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='room.pk')
    room_slug = serializers.SlugField(source='room.room_slug')
    customer_id = serializers.IntegerField(source='customer.pk')
    customer_name = serializers.CharField(source='customer.username')

    class Meta:
        model = CheckIn
        fields = ('phone_number', 'email', 'customer_id', 'customer_name', 'room_id', 'room_slug',)

        # blog

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ( 'author', 'body', 'created_at',)
        model = Post

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Profile

class AboutSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ( 'desc', 'mission', 'vision',)
        model = About