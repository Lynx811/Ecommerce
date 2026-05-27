from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product

def get_cart(user):
    # Check if the user already has a cart
    cart = Cart.objects.filter(user=user).first()

    if cart:
        # If the cart exists, ensure it is active
        if not cart.is_active:
            print(f"Cart for user {user} was inactive, activating it.")
            cart.is_active = True  # Activate the cart if it's inactive
            cart.save()  # Save the changes to the cart
        print(f"User {user} already has an active cart: {cart}")
        return cart
    else:
        # If no cart exists for the user, create a new active cart
        print(f"No cart found for user {user}, creating a new cart.")
        cart = Cart.objects.create(user=user, is_active=True)
        return cart


@login_required
def cart_view(request):
    cart = get_cart(request.user)  # Get the user's cart
    items = cart.cartitem_set.all()  # Get items in the cart
    
    # Calculate the total price of the cart items
    total_price = sum(item.subtotal() for item in items) if items else 0
    
    return render(request, 'cart/cart.html', {'cart': cart, 'items': items, 'total_price': total_price})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request.user)  # Retrieve the user's cart

    # Check if the product is already in the cart, and update the quantity
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:  # If the item already exists in the cart, increase the quantity
        print(f"Item already in cart, increasing quantity for {item.product.name}.")
        item.quantity += 1
        item.save()

    return redirect('cart:cart')  # Redirect to cart view


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    
    # Ensure the item belongs to the logged-in user
    if item.cart.user == request.user:
        item.delete()  # Remove the item from the cart
    
    return redirect('cart:cart')  # Redirect to cart view


@login_required
def update_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)
    
    # Ensure the item belongs to the logged-in user
    if item.cart.user == request.user:
        if action == 'increase':
            item.quantity += 1  # Increase the quantity
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1  # Decrease the quantity, but don't go below 1
        item.save()  # Save the updated quantity
    
    return redirect('cart:cart')  # Redirect to cart view
