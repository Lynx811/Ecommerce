from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.http import JsonResponse

# Product list view
def product_list(request):
    """Fetch all products and render the list"""
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

# Product detail view
def product_detail(request, pk):
    """Fetch and display a single product's details"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

# Category detail view
def category_list(request, id):
    """Fetch and display products by category"""
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    return render(request, 'core/category_list.html', {'category': category, 'products': products})

# Search results view
def search_results(request):
    """Fetch and display products based on the search query"""
    query = request.GET.get('q', '')  # Get the search term
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'core/search_results.html', {'products': products, 'query': query})

# AJAX search view for real-time search suggestions
def ajax_search(request):
    """Handle AJAX search requests and return JSON results"""
    query = request.GET.get('q', '')
    results = []

    if query:
        products = Product.objects.filter(name__icontains=query)
        results = [
            {"name": product.name, "price": float(product.price), "image": product.image.url}
            for product in products
        ]

    return JsonResponse({"results": results})

def product_list(request):
    # Fetch all products from the database
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})