from django.contrib import admin
from .models import Cart, CartItem

# Register the Cart model
admin.site.register(Cart)
admin.site.register(CartItem)
