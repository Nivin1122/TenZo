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
    path('update_order_status/<int:order_id>',views.update_order_status, name = 'update_order_status')
]