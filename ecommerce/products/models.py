from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', default='products/default.jpg')
    description = models.TextField()
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'  # This allows accessing related products from a category using `category.products.all()`
    )

    def __str__(self):
        return self.name
