from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from .models import Post, About, Profile, Room, Booking, CheckIn, Order
from .serializers import PostSerializer, AboutSerializer, ProfileSerializer, RoomSerializer, BookingSerializer, CheckinSerializer
from .permissions import IsAuthorOrReadOnly
from django.contrib.auth.decorators import login_required
import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from rest_framework.views import APIView
from rest_framework.response import Response
import json
import base64

# booking

class RoomView(generics.ListAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.order_by('-id')


class RoomDetailView(generics.RetrieveAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    lookup_field = 'room_slug'


class BookingCreateApiView(generics.CreateAPIView):
    # permission_classes = (IsAuthenticated, )
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def create(self, request, *args, **kwargs):
        response = {}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response['data'] = serializer.data
        response['response'] = "Room is successfully booked"
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=request.data['room'])
        if room.is_booked:
            return Response({"response": "Room is already booked"}, status=status.HTTP_200_OK)
        room.is_booked = True
        room.save()
        checked_in_room = CheckIn.objects.create(
            customer=request.user,
            room=room,
            phone_number=request.data['phone_number'],
            email=request.data['email']
        )
        checked_in_room.save()
        return self.create(request, *args, **kwargs)


class CheckoutView(APIView):
    def post(self, request):
        room = get_object_or_404(Room, pk=request.data['pk'])
        checked_in_room = CheckIn.objects.get(room__pk=request.data['pk'])
        print(checked_in_room)
        room.is_booked = False
        room.save()
        return Response({"Checkout Successful"}, status=status.HTTP_200_OK)


class CheckedInView(generics.ListAPIView):
    # permission_classes = (IsAdminUser, )
    serializer_class = CheckinSerializer
    queryset = CheckIn.objects.order_by('-id')


class PostList(generics.ListCreateAPIView):

    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class AboutList(generics.ListCreateAPIView):

    queryset = About.objects.all()
    serializer_class = AboutSerializer

# @login_required
class ProfileList(generics.ListCreateAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

def email_confirm_redirect(request, key):
    return HttpResponseRedirect(
        f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/"
    )


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


# payment

def PaypalToken(client_ID, client_Secret):
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "client_id": client_ID,
        "client_secret": client_Secret,
        "grant_type": "client_credentials"
    }
    # Encode client_ID and client_Secret as byte-like objects
    auth_string = f"{client_ID}:{client_Secret}".encode('utf-8')
    # Encode the auth_string using base64
    encoded_auth_string = base64.b64encode(auth_string).decode('utf-8')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_auth_string}"
    }

    token = requests.post(url, data, headers=headers)
    return token.json()['access_token']


clientID = 'Ac0TcWWSWtIXYoY7zcxdwwWR1MTsWOmFasUvygUtADsutxUWjuK5Or-KscuWF9-22K2r0hGC3d80yga3'
clientSecret = 'ELkg81DJbcQ0I_xECHtcprqrNHp4-5fzjmoPNUbNcUP5uKu-6s_IZq9xQK5s1yyUis2RYB_wDzNU5H7B'


class CreateOrderViewRemote(APIView):

    def get(self, request):
        token = PaypalToken(clientID, clientSecret)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+token,
        }
        json_data = {
             "intent": "CAPTURE",
             "a lication_context": {
                 "notify_url": "https://pesapedia.co.ke",
                 "return_url": "https://pesapedia.co.ke",#change to your doma$
                 "cancel_url": "https://pesapedia.co.ke", #change to your domain
                 "brand_name": "PESAPEDIA SANDBOX",
                 "landing_page": "BILLING",
                 "shipping_preference": "NO_SHIPPING",
                 "user_action": "CONTINUE"
             },
             "purchase_units": [
                 {
                     "reference_id": "294375635",
                     "description": "African Art and Collectibles",

                     "custom_id": "CUST-AfricanFashion",
                     "soft_descriptor": "AfricanFashions",
                     "amount": {
                         "currency_code": "USD",
                         "value": "200" #amount,
                     },
                 }
             ]
         }
        response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)
        order_id = response.json()['id']
        linkForPayment = response.json()['links'][1]['href']
        return Response(linkForPayment)

class CaptureOrderView(APIView):
    def get(self, request):
        token = request.data.get('token')
        captureurl = request.data.get('url')
        
        if captureurl is None:
            # Handle the case when 'url' key is missing or has a value of None
            # Return an appropriate response or raise an exception
            # For example:
            return Response({'error': 'Missing or invalid capture URL.'}, status=400)
        
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
        response = requests.post(captureurl, headers=headers)
        return Response(response.json())


# @csrf_exempt
# def create_payment(request):
#     amount = request.POST.get('amount')
    
#     # Create the order in the database
#     order = Order.objects.create(amount=amount)
    
#     # Set up PayPal API request
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {settings.PAYPAL_ACCESS_TOKEN}',
#     }
    
#     data = {
#         'intent': 'CAPTURE',
#         'purchase_units': [{
#             'amount': {
#                 'currency_code': 'USD',
#                 'value': str(amount),
#             }
#         }],
#         'application_context': {
#             'return_url': 'http://localhost:3000/payment/success',
#             'cancel_url': 'http://localhost:3000/payment/cancel',
#         }
#     }
    
#     # Make the API request to create a payment
#     response = requests.post('https://api.sandbox.paypal.com/v2/checkout/orders', headers=headers, data=json.dumps(data))
#     response_data = response.json()
    
#     # Store the PayPal order ID in the database
#     order.paypal_order_id = response_data['id']
#     order.save()
    
#     # Return the PayPal approval URL to the frontend
#     return JsonResponse({'approval_url': response_data['links'][1]['href']})

# @csrf_exempt
# def payment_success(request):
#     order_id = request.GET.get('order_id')
    
#     # Retrieve the order from the database
#     order = Order.objects.get(paypal_order_id=order_id)
    
#     # Mark the order as completed
#     order.is_completed = True
#     order.save()
    
#     return JsonResponse({'message': 'Payment successful'})

# @csrf_exempt
# def payment_cancel(request):
#     return JsonResponse({'message': 'Payment canceled'})


# Paypal view
'''

class PaypalPaymentView(APIView):
    """
    endpoint for create payment url
    """
    def post(self, request, *args, **kwargs):
        amount=20 # 20$ for example
        status,payment_id,approved_url=make_paypal_payment(amount=amount,currency="USD",return_url="https://example.com/payment/paypal/success/",cancel_url="https://example.com")
        if status:
            handel_subscribtion_paypal(plan=plan,user_id=request.user,payment_id=payment_id)
            return Response({"success":True,"msg":"payment link has been successfully created","approved_url":approved_url},status=201)
        else:
            return Response({"success":False,"msg":"Authentication or payment failed"},status=400)
        
class PaypalValidatePaymentView(APIView):
    """
    endpoint for validate payment 
    """
    permission_classes=[permissions.IsAuthenticated,]
    def post(self, request, *args, **kwargs):
        payment_id=request.data.get("payment_id")
        payment_status=verify_paypal_payment(payment_id=payment_id)
        if payment_status:
            # your business logic 
             ...
            return Response({"success":True,"msg":"payment improved"},status=200)
        else:
            return Response({"success":False,"msg":"payment failed or cancelled"},status=200)

            '''