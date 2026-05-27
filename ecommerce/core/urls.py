from django.urls import include, path
from . import views
from .views import home, category_list, product_detail, logout_user, search_results

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('category/<int:id>/', views.category_list, name='category_list'),  # Category page
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('logout/', views.logout_user, name='logout'),  # Add logout URL here
    path('product/', include('products.urls')),  # No namespace here
    path('search/', search_results, name='search_results'),  # New search results page
]
