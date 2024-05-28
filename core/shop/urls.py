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
    path('checkout/',views.checkout, name="checkout"),
    path('place_order/', views.place_order, name='place_order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.list_orders, name='list_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', views.cancel_orders, name='cancel_orders'),

]