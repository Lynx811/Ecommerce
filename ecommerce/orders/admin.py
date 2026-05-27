from django.core.mail import send_mail
from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shipping_status', 'payment_status', 'total_price', 'created_at')
    list_filter = ('shipping_status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__username', 'shipping_address')
    ordering = ('-created_at',)
    list_editable = ('shipping_status', 'payment_status')
    readonly_fields = ('created_at', 'total_price', 'estimated_delivery_date')

    def save_model(self, request, obj, form, change):
        """Automatically send notifications when order status changes."""
        if 'shipping_status' in form.changed_data:
            send_mail(
                f"Order #{obj.id} Status Update",
                f"Dear {obj.user.username},\n\nYour order status has been updated to: {obj.shipping_status}.",
                "yourshop@example.com",
                [obj.user.email],
                fail_silently=True,
            )
        
        if 'payment_status' in form.changed_data and obj.payment_status == "Paid":
            send_mail(
                f"Payment Received for Order #{obj.id}",
                f"Dear {obj.user.username},\n\nWe have received your payment. Your order is being processed.",
                "yourshop@example.com",
                [obj.user.email],
                fail_silently=True,
            )

        super().save_model(request, obj, form, change)

admin.site.register(Order, OrderAdmin)
