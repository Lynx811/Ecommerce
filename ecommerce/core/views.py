from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Category, Product


# Home view
def home(request):
    query = request.GET.get('q', '')  # Get the search query from the URL
    categories = Category.objects.all()  # Fetch all categories
    
    if query:
        # Filter products based on the search query
        products = Product.objects.filter(name__icontains=query)
    else:
        # Show all products if no query
        products = Product.objects.all()

    return render(request, 'core/home.html', {
        'products': products,
        'categories': categories,
        'query': query
    })

# Logout view
@login_required
def logout_user(request):
    logout(request)  # type: ignore # Logs out the user
    return redirect('home')  # Redirect to the homepage after logout

# Category view to list products in that category
def category_list(request, id):
    # Get the category by ID
    category = get_object_or_404(Category, id=id)
    
    # Get all products for this category
    products = Product.objects.filter(category=category)
    
    # Render the category page template
    return render(request, 'core/category_list.html', {
        'category': category,
        'products': products
    })

# Product detail view
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'core/product_detail.html', {'product': product})

def search_results(request):
    query = request.GET.get('q', '')  
    categories = Category.objects.all()  

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'core/search_results.html', {
        'products': products,
        'categories': categories,
        'query': query
    })


