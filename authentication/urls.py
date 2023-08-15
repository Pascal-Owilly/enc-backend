from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)
from authentication.views import email_confirm_redirect, password_reset_confirm_redirect
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path
from authentication import views

from django.conf import settings
from django.conf.urls.static import static
from .views import PostList, PostDetail, AboutList, ProfileList, RoomView, RoomDetailView, BookingCreateApiView, CheckoutView, CheckedInView
# from .views import create_payment, payment_success, payment_cancel



urlpatterns = [

    # Blog posts

    path('blog-posts/<int:pk>/', PostDetail.as_view()),
    path('blog-posts/', PostList.as_view()),
    path('about/', AboutList.as_view()),
    path('profile/', ProfileList.as_view()),

    # booking

    path('get_room_list/', RoomView.as_view(), name="room_list"),
    path('get_a_room_detail/<str:room_slug>/', RoomDetailView.as_view(), name="single_room"),
    path('book/', BookingCreateApiView.as_view(), name='book_room'),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('get_current_checked_in_rooms/', CheckedInView.as_view(), name="checked_in_rooms"),

    #  authentication

    path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("register/resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/<str:uidb64>/<str:token>/", password_reset_confirm_redirect, name="password_reset_confirm",
    ),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # payment
    path('paypal/create/order', views.CreateOrderViewRemote.as_view(), name='create_payment'),
    path('paypal/capture/order', views.CaptureOrderView.as_view(), name='capture_payment'),

    # path('payment/success/', payment_success, name='payment_success'),
    # path('payment/cancel/', payment_cancel, name='payment_cancel'),

    # path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    # path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),

]



