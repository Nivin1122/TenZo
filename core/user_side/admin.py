from django.contrib import admin
from . models import Customuser,Otp,Address

# Register your models here.
admin.site.register(Customuser)
admin.site.register(Otp)
admin.site.register(Address)