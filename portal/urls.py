from django.urls import path
from . import views

urlpatterns  = [
    path('connect/', views.connect_view, name='connect_view'), # nickname the url for later use
    path('wait/<uuid:session_id>/', views.wait_for_payment_view, name='wait_for_payment_view'), # nickname the url for later use
]
