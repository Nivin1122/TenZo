from django.db import models
from django.contrib.auth.models import AbstractUser,User


# Create your models here.
class Customuser(AbstractUser):
    is_blocked = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    

class Otp(models.Model):
    otp = models.CharField(max_length=6)
    buyer = models.OneToOneField(Customuser, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.otp


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    user = models.ForeignKey(Customuser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True)
    phone_no = models.IntegerField(null=True)


    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zipcode}, {self.country}"
    
