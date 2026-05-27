from django.urls import path
from . import views
from .views import ajax_search

app_name = 'products'  # Define the namespace here


urlpatterns = [
    
    path('category/<int:category_id>/', views.category_list, name='category_detail'),  # New URL pattern
     path('', views.product_list, name='product_list'),  # List view of products
    path('product/<int:pk>/', views.product_detail, name='product_detail'),  # Detail view
  path('ajax_search/', ajax_search, name='ajax_search'),  # New AJAX search route
]

