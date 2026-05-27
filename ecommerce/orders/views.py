from datetime import timedelta
import json
import logging
import traceback
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from cart.models import Cart, CartItem
from .models import Order, OrderItem, Address

logger = logging.getLogger(__name__)

def send_order_email(user, order, subject, message):
    """Helper function to send order-related emails."""
    if user.email:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.send(fail_silently=False)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import logging

from cart.models import Cart, CartItem  # Import from the correct app
from .models import Address, Order, OrderItem
 # Ensure this function is correctly defined

logger = logging.getLogger(__name__)
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    print(f"🛒 Checkout - Found Active Cart: {cart}")

    # Get cart items as a list to ensure they are properly fetched
    cart_items = list(CartItem.objects.filter(cart=cart))
    print(f"🛒 Checkout - Cart Items: {cart_items}")  # Debugging print

    # Ensure cart is not empty
    if not cart_items:
        print("🚨 Checkout Error: Cart is empty at this stage!")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "message": "Your cart is empty."}, status=400)
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        try:
            print("📝 Received POST Data:", request.POST)
            shipping_address_id = request.POST.get('shipping_address', '').strip()
            shipping_method = request.POST.get('shipping_method', '').strip()
            payment_method = request.POST.get('payment_method', '').strip()

            logger.debug(f"Received checkout data: {request.POST}")

            # Ensure all fields are filled
            if not shipping_address_id or not shipping_method or not payment_method:
                error_msg = "Please complete all required fields."
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "message": error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('orders:checkout')

            shipping_address = get_object_or_404(Address, id=shipping_address_id, user=request.user)
            payment_status = 'Paid' if payment_method == 'Pay Now' else 'Pending'

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    cart=cart,
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    total_price=cart.total_price(),
                    estimated_delivery_date=timezone.now().date() + timedelta(days=7)
                )

                # Bulk create order items
                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_at_purchase=item.product.price
                    ) for item in cart_items
                ])

                # 🔥 Ensure total price updates
                order.total_price = order.calculate_total_price()
                order.save(update_fields=['total_price'])

                # Mark cart as inactive and clear cart items
                cart.is_active = False
                cart_items.clear()  # This clears the list, but we should delete items explicitly
                CartItem.objects.filter(cart=cart).delete()
                cart.save(update_fields=['is_active'])

                # Send email confirmation
                subject = "Order Confirmation"
                message = f"""
Dear {request.user.username},

Thank you for your order! Here are your order details:

Order ID: {order.id}
Shipping Address: {shipping_address}
Shipping Method: {shipping_method}
Estimated Delivery Date: {order.estimated_delivery_date.strftime('%Y-%m-%d')}
Total Price: Ksh{order.total_price}
Payment Status: {order.payment_status}

Best regards,
Your Store Team
                """
                send_order_email(request.user, order, subject, message)

                confirmation_url = reverse('orders:order_confirmation', kwargs={'order_id': order.id})

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True, "redirect_url": confirmation_url})

                messages.success(request, "Your order has been placed successfully.")
                return redirect(confirmation_url)

        except Exception as e:
            logger.error(f"Checkout failed for user {request.user.username}: {str(e)}", exc_info=True)
            traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "message": "An error occurred during checkout. Please try again."}, status=500)

            messages.error(request, "An error occurred during checkout. Please try again.")
            return redirect('orders:checkout')

    saved_addresses = Address.objects.filter(user=request.user)

    total_price = cart.total_price()
    print(f"✅ Debug: Total Price Calculated: {total_price}")  # Debugging print
    
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'saved_addresses': saved_addresses,
        'total_price': cart.total_price(),
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):  # Matches 'order_id' in urls.py
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.shipping_status in ["Pending", "Processing"]:
        order.shipping_status = "Canceled"
        order.save()
        messages.success(request, "Your order has been canceled successfully.")
    else:
        messages.error(request, "You can only cancel pending or processing orders.")

    return redirect(reverse('orders:order_history'))

@login_required
@csrf_exempt
def save_address(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)

        # Extract and sanitize fields
        street = data.get("street_address", "").strip()
        city = data.get("city", "").strip()
        state = data.get("state", "").strip()
        postal_code = data.get("postal_code", "").strip()
        country = data.get("country", "").strip()

        # Validate required fields
        if not all([street, city, state, postal_code, country]):
            return JsonResponse({"success": False, "message": "All fields are required!"}, status=400)

        # Save address in the database
        try:
            address = Address.objects.create(
                user=request.user,
                street_address=street,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country
            )

            return JsonResponse({
                "success": True,
                "address_id": address.id,
                "full_address": f"{street}, {city}, {state}, {postal_code}, {country}"
            })

        except ValidationError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON from request
            street = data.get("street_address")
            city = data.get("city")
            state = data.get("state")
            postal_code = data.get("postal_code")
            country = data.get("country")

            if street and city and state and postal_code and country:
                address = Address.objects.create(
                    user=request.user,
                    street_address=street,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country
                )

                return JsonResponse({
                    "success": True,
                    "address_id": address.id,
                    "full_address": f"{street}, {city}, {state}, {postal_code}, {country}"
                })  # Return JSON instead of redirecting
            else:
                return JsonResponse({"success": False, "message": "Missing fields"})
        
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})