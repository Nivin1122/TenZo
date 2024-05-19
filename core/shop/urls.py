from django.contrib import admin
from django.urls import path,include
from.import views

urlpatterns = [
    path('',views.index, name='index'),
    path('all_products/', views.all_products, name="all_products"),
    path('product_details/<int:id>/', views.product_details, name='product_details'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.list_cart, name='cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/',views.checkout, name="checkout")

]