from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Represents a product category
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    A purchasable item in the store
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    #current stock level, gets reduced when an order is completed
    stock = models.PositiveIntegerField()

    #products can belong to categories, but not mandatory right now
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    #product imagess stored in the MEDIA_ROOT/products
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Represents a user cart or completed order.
    When 'complete=False', the shopping cart is active.
    When the order is completed, stock gets deducted from the product inventory
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #this controls the cart being active or not
    complete = models.BooleanField(default=False)

    @property
    def total_price(self):
        """
        Returns the combined cost of all items in the order
        """
        return sum(item.subtotal() for item in self.items.all())
    
    @property
    def total_quantity(self):
        """
        Returns the total number of items
        """
        return sum(item.quantity for item in self.items.all())
    

class OrderItem(models.Model):
    """
    Represents a single product within an order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    #the quantity ordered for the product
    quantity = models.PositiveIntegerField(default=0)

    def subtotal(self):
        return self.product.price * self.quantity