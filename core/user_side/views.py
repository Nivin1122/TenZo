from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import  login, logout
from django.http import HttpResponse
from .models import Customuser,Address
from product_side.models import Cart,Product
from django.contrib import messages
from django.contrib.auth.models import User
import pyotp
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password





# Create your views here.
@never_cache
def user_login(request):
    
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect("/")
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username = username, password = password)
    
        if user is not None and not user.is_superuser:
            login(request,user)
            return redirect('index')

        else:
            messages.error(request, 'username or password is incorrect')
        
    return render(request, 'user_login.html')

def user_out(request):
    logout(request)
    return redirect("/")


@never_cache
def user_signup(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        validation_error = False
        context = dict()

        if Customuser.objects.filter(username = username).exists():
            validation_error = True
            
            context["username_exists"] = True

        if Customuser.objects.filter(email = email).exists():
            validation_error = True

            context["email_exists"] = True


        if validation_error:
            context["username"] = username
            context["email"] = email
            return render(request, 'user_signup.html', context=context)

        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        send_mail(
            'OTP for Email Verification',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        created_time = str(datetime.today())
        request.session['otp'] = otp
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = pass1
        request.session['created_at'] = created_time

        return redirect('verify_otp')

    return render(request, 'user_signup.html')

@never_cache
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect("/")
    elif not (request.session.get('email') and request.session.get('otp')):
            return redirect("/user_login/")
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        stored_time = request.session.get('created_at')
        created_at = datetime.strptime(stored_time, '%Y-%m-%d %H:%M:%S.%f')
        current_time = datetime.today()

        difference = current_time - created_at
        seconds = difference.seconds
        minutes = seconds/60

        email = request.session.get('email')

        if minutes < 5:
            if entered_otp == stored_otp:
                username = request.session.get('username')
                password = request.session.get('password')

                user = Customuser.objects.create_user(username=username, password=password, email=email)

                del request.session['otp']
                del request.session['username']
                del request.session['email']
                del request.session['password']
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Invalid OTP")
                return redirect('verify_otp')

        else:
            messages.error(request, "OTP Expired. New OTP sent to your mail")
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            send_mail(
                'OTP for Email Verification',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            request.session['otp'] = otp
            request.session['created_at'] = str(datetime.today())
            return redirect('verify_otp')
        
    return render(request, 'verify_otp.html')

def resend_otp(request):
    email = request.session.get('email')
    if not email:
        return redirect("/user_login/")
    
    elif not (request.session.get('email') and request.session.get('otp')):
            return redirect("/user_login/")
    messages.success(request, "OTP sent successfully. Enter the new OTP")

    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    send_mail(
        'OTP for Email Verification',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    request.session['otp'] = otp
    request.session['created_at'] = str(datetime.today())
    return redirect('verify_otp')



def profile(request):
    return render(request, 'profile.html')



@login_required
def edit_user_profile(request):
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        
        if not first_name or not last_name or not username:
            messages.error(request, 'All fields are required.')
            return render(request, 'edit_user_profile.html', {'user': user})
        
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    else:
        return render(request, 'edit_user_profile.html', {'user': user})
    



def add_user_address(request):
    user = request.user
    print(user)
    if request.method == 'POST':
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')
        name = request.POST.get('name')
        phone_no = request.POST.get('phone_no')

        address = Address.objects.create(
            street=street,
            city=city,
            state=state,
            zipcode=zipcode,
            country=country,
            user=user,
            name=name,
            phone_no=phone_no
        )

        messages.success(request, 'Address saved successfully.')

        return redirect('checkout') 
    
    return render(request, 'add_user_address.html')



def edit_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)

    if request.method == 'POST':
        
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')
        name = request.POST.get('name')
        phone_no = request.POST.get('phone_no')

        
        address.street = street
        address.city = city
        address.state = state
        address.zipcode = zipcode
        address.country = country
        address.name=name
        address.phone_no=phone_no

        address.save()

        
        messages.success(request, 'Address updated successfully.')

        
        return redirect('users_address')

    return render(request, 'edit_address.html', {'address': address})





def users_address(request):

    user = request.user
    address = Address.objects.filter(user=user)
    print(user)

    return render(request, 'users_address.html', {'address': address})


def delete_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)

    if request.method == 'POST':
        address.delete()

        return redirect('users_address')
    
    return render(request, 'users_address.html')




@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('change_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.', extra_tags='error_confirm_password')
            return redirect('change_password')
        
        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.', extra_tags='error_current_password')
            return redirect('change_password')
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error, extra_tags='error_new_password')
            return redirect('change_password')
        
        user.set_password(new_password)
        user.save()
        
        update_session_auth_hash(request, user) 
        messages.success(request, 'Your password was successfully updated!')
        return redirect('index')
    
    return render(request, 'change_password.html')