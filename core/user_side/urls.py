from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('user_login/',views.user_login, name = 'user_login'),
    path('user_logout/',views.user_out, name = 'user_loout'),
    path('user_signup/', views.user_signup, name = 'user_signup'),
    path('verify_otp/', views.verify_otp, name = 'verify_otp'),
    path('resend_otp/', views.resend_otp, name = 'resend_otp'),
    path('profile/',views.profile, name = 'profile'),
    path('edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),
    path('add_user_address/', views.add_user_address, name='add_user_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('users_address/', views.users_address, name='users_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name = 'delete_address'),

]