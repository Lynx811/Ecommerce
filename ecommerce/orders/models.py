from django.db import models
from django.conf import settings
from cart.models import Cart
from products.models import Product
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.country}"



class Order(models.Model):
    ORDER_STATUS = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    SHIPPING_METHODS = [
        ('Standard', 'Standard'),
        ('Express', 'Express'),
    ]

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Pay Now', 'Pay Now'),
        ('Pay on Delivery', 'Pay on Delivery'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default='Standard')
    shipping_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    estimated_delivery_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='Pay on Delivery'
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    def calculate_total_price(self):
        return sum(item.subtotal for item in self.order_items.all())

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the order is new before saving

        super().save(*args, **kwargs)  # First save to generate an ID

        # Ensure Express shipping requires 'Pay Now'
        if self.shipping_method == 'Express' and self.payment_method != 'Pay Now':
            raise ValidationError("Express shipping requires 'Pay Now' payment method.")

        # Automatically set estimated delivery date
        if self.shipping_method == 'Standard':
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=5)
        elif self.shipping_method == 'Express':
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=2)

        # Recalculate total price
        self.total_price = self.calculate_total_price()
        super().save(update_fields=['total_price'])

        # Mark cart as inactive after order placement
        self.cart.is_active = False
        self.cart.save(update_fields=['is_active'])



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        print(f"🔄 Saving OrderItem (ID: {self.id})")  # Debug print

        # Ensure price_at_purchase is set
        if not self.price_at_purchase or self.price_at_purchase == 0:
            self.price_at_purchase = self.product.price  

        super().save(*args, **kwargs)  

        # 🔥 Update Order total price
        print(f"🔄 Updating Order (ID: {self.order.id}) total price")  # Debug print
        self.order.update_total_price()
        print(f"✅ New Total Price: {self.order.total_price}")  # Debug print

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase  # ✅ Dynamically calculate subtotal

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
  



 

class Shipping(models.Model):
    order = models.ForeignKey(Order, related_name='shipping_details', on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    shipping_status = models.CharField(max_length=20, choices=Order.ORDER_STATUS, default='Pending')

    def update_shipping_status(self, new_status):
        self.shipping_status = new_status
        self.save()

    def __str__(self):
        return f"Shipping for Order {self.order.id}"
