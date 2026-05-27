# orders/urls.py
from django.urls import path
from . import views
from .views import cancel_order, save_address

from .views import checkout, order_history, order_detail, order_confirmation  # Import the views


app_name = 'orders'

urlpatterns = [
   path('checkout/', views.checkout, name='checkout'),
    path('history/', views.order_history, name='order_history'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path("save-address/", save_address, name="save_address"),
]
