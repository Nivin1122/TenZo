from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
from user_side.models import Customuser,Address
from django.core.management.base import BaseCommand




# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=200)
    is_listed = models.BooleanField(default=True)


    def __str__(self):
        return self.name
    

    

class Product(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="img/",blank=True, null=True)
    image2 = models.ImageField(upload_to="img/",blank=True, null=True)
    image3 = models.ImageField(upload_to="img/",blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_listed = models.BooleanField(default=True)
    category = models.ForeignKey(Category,null=True, on_delete=models.CASCADE)
    max_quantity = models.PositiveIntegerField(default=5)
    
    

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} in cart of {self.cart.user.username}"

    def get_total_price(self):
        return self.product.price * self.quantity
    


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=(
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment')
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default='Pending')
    
    def __str__(self):
        return f"Order {self.id}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} in order {self.order.id}"