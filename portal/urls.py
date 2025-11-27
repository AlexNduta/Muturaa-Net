from django.urls import path
from . import views

urlpatterns  = [
    # This is our connect url where the user will be required to key-in their phone number
    path('connect/', views.connect_view, name='connect_view'), # nickname the url for later use
    # This is the waitting page
    path('wait/<uuid:session_id>/', views.wait_for_payment_view, name='wait_for_payment_view'), # nickname the url for later use
   # The callback url that safaricom will use to send succesful messages
    path('callback/mpesa/', views.mpesa_callback_view, name='mpesa_callback_view'),
    path('check-status/<uuid:session_id>', views.check_payment_status_view, name='check_payment_status_view'),
]
