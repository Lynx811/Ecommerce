from django.db import models
from django.conf import settings
from django.utils.timezone import now
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now)  # Set the current time by default

    def total_price(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())

    def total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart of {self.user.username} ({'Active' if self.is_active else 'Inactive'})"

    @classmethod
    def get_or_create_active_cart(cls, user):
        """Ensures only one active cart per user, reactivating an existing cart if necessary."""
        active_cart = cls.objects.filter(user=user, is_active=True).first()

        if active_cart:
            return active_cart  # Return the already active cart

        # Check if an inactive cart exists and reactivate it
        inactive_cart = cls.objects.filter(user=user, is_active=False).first()
        if inactive_cart:
            inactive_cart.is_active = True
            inactive_cart.save()
            return inactive_cart

        # Create a new cart only if no cart exists
        return cls.objects.create(user=user, is_active=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
