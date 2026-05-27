from .models import Cart

def cart_summary(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            # Count the number of distinct products in the cart
            item_count = cart.cartitem_set.count()
        else:
            item_count = 0
    else:
        item_count = 0  # Handle guests or unauthenticated users here
    return {'cart_item_count': item_count}
