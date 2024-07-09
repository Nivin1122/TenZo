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
    path('cart/increase/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('checkout/',views.checkout, name="checkout"),
    path('place_order/', views.place_order, name='place_order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.list_orders, name='list_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', views.cancel_orders, name='cancel_orders'),
    path('order/item/cancel/<int:order_item_id>/', views.cancel_order_item, name='cancel_order_item'),

    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('wallet/', views.wallet_detail, name='wallet_detail'),
    path('generatePdf/<int:order_id>/', views.generatePdf, name='generatePdf'),
]