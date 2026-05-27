from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from orders.models import Order, OrderItem

@receiver(post_save, sender=OrderItem)
def validate_order_items(sender, instance, **kwargs):
    """
    Ensure the order has items after an OrderItem is saved.
    """
    order = instance.order
    if not OrderItem.objects.filter(order=order).exists():
        raise ValidationError("Cannot place an order without items.")
