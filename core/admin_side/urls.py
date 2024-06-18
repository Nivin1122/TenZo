from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('admin_home/',views.admin_home, name ='admin_home'),
    path('admin_login/', views.admin_login, name ='admin_login'),
    path('category/',views.category, name ='category'),
    path('category_listing/<int:id>',views.category_listing, name ='category_listing'),
    path('category_adding', views.category_adding, name ='category_adding'),
    path('category_editing/<int:category_id>', views.category_editing, name ='category_editing'),
    path('users/',views.users, name ='users'),
    path('users_block/<int:id>',views.users_block, name ='users_block'),
    path('users_unblock/<int:id>',views.users_unblock, name ='users_unblock'),
    path('admin_products/',views.admin_products,name="admin_products"),
    path('listing_admin_products/<int:id>',views.listing_admin_products, name='listing_admin_products'),
    path('adding_admin_products/',views.adding_admin_products, name='adding_admin_products'),
    path('editing_admin_products/<int:category_id>',views.editing_admin_products, name='editing_admin_products'),

    path('admin_order_list/', views.admin_order_list, name='admin_order_list'),
    path('update_order_status/<int:order_id>',views.update_order_status, name = 'update_order_status'),
    path('orders/<int:order_id>/', views.order_details_admin, name='order_details_admin'),

    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('coupon_manage/', views.coupon_manage, name='coupon_manage'),
    path('deactivate_coupon/<int:coupon_id>/', views.deactivate_coupon, name='deactivate_coupon'),
    path('activate_coupon/<int:coupon_id>/', views.activate_coupon, name='activate_coupon'),

    path('generatePdf/', views.generatePdf, name='generate_pdf'),
    path('generateExcel/', views.generateExcel, name='generate_excel'),
    path('admin_offers/', views.admin_offers, name='admin_offers'),
    path('add_offer/', views.add_offer, name='add_offer'),
    path('assign_offer_to_product/', views.assign_offer_to_product, name='assign_offer_to_product'),
]