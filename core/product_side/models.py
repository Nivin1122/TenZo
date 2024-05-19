from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
from user_side.models import Customuser
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
    stock = models.IntegerField(default=0)
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
    


