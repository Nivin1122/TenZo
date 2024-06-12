from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from user_side.models import Customuser
from product_side.models import Category,Product,Order,Offer,Coupon
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum,Count
from datetime import datetime
from django.utils import timezone
from reportlab.pdfgen import canvas



# Create your views here.
def admin_home(request):
    overall_sales_count = Order.objects.aggregate(total_sales=Count('total_price'))['total_sales'] or 0
    overall_order_amount = Order.objects.aggregate(total_order_amount=Sum('total_price'))['total_order_amount'] or 0

    # Sales report logic
    today = timezone.now()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    period = request.GET.get('period', 'month')

    if start_date_str and end_date_str:
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        if period == 'day':
            start_date = today - timezone.timedelta(days=1)
        elif period == 'week':
            start_date = today - timezone.timedelta(weeks=1)
        elif period == 'month':
            start_date = today - timezone.timedelta(days=30)
        elif period == 'year':
            start_date = today - timezone.timedelta(days=365)
        else:
            return render(request, 'invalid_period.html')

        end_date = today

    orders = Order.objects.filter(created_at__range=[start_date, end_date])

    total_sales_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    # total_discount_amount = orders.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    context = {
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_sales_amount': total_sales_amount,
        # 'total_discount_amount': total_discount_amount,
        'total_sales_count': total_sales_count,
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
    }

    return render(request, 'admin_home.html', context)
    


@never_cache
def admin_login(request):

    if request.method == 'POST':

        username = request.POST.get("uname")
        password = request.POST.get("pass")

        user = authenticate(request, username = username, password = password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_home')
        

        else:
            messages.error(request, "username or password is not correct")
            
            
    return render(request, 'admin_login.html')



def category(request):

    categories = Category.objects.all().order_by('-id')

    context = {
        "categories" : categories
    }
    return render(request,'category.html',context)



def category_listing(request,id):

    if request.method == "POST":

        category_id = id

        category = Category.objects.get(id=category_id)
        category.is_listed = not category.is_listed
        
        category.save()
        return redirect('category') 

    return render(request, 'category.html')





def category_adding(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')

        category_description = request.POST.get('category_description')

        new_category = Category.objects.create(name = category_name, description = category_description)

        return redirect('category') 
    return render(request, 'category_adding.html')





def category_editing(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')

        category.description = request.POST.get('description')

        category.save()
        return redirect('category')
    
    context = {
        'category' : category
    }

    return render(request, 'category_editing.html',context)





def users(request):

    all_users = Customuser.objects.all().order_by()
    
    context = {
        "all_users" : all_users
    }

    return render (request, 'users.html',context)


def users(request):
    all_users = Customuser.objects.all().order_by()
    context = {
        "all_users": all_users
    }
    return render(request, 'users.html', context)


def users_block(request, id):
    if request.method == 'POST':
        user_id = id
        user = Customuser.objects.get(id=user_id)
        user.is_blocked = True

        user.save()

    return redirect('users')

def users_unblock(request, id):
    if request.method == 'POST':
        user_id = id

        user = Customuser.objects.get(id=user_id)
        user.is_blocked = False
        user.save()

    return redirect('users')



def admin_products(request):
    products = Product.objects.all().order_by('-id')

    context = {
        'products' : products
    }

    return render(request,'admin_products.html',context)



def listing_admin_products(request,id):
    if request.method == 'POST':
        product_id = id
        products = Product.objects.get(id=product_id)

        products.is_listed = not products.is_listed
        print(products.is_listed)
        products.save()
        return redirect('admin_products')

    return render(request, 'admin_products.html')



def editing_admin_products(request, category_id):
    product = get_object_or_404(Product, id=category_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
   
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, id=category_id)


        product.category = category


        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.image = request.FILES.get('image')
        product.image2 = request.FILES.get('image2')
        product.image3 = request.FILES.get('image3')
 
        product.save()

        return redirect('admin_products')
    
    context = {
        'product': product,
        'categories': categories,
        'existing_category_id': product.category.id if product.category else None,
    }

    return render(request, 'editing_admin_products.html', context)



def adding_admin_products(request):
    categories = Category.objects.all()

    context = {
        'categories' : categories
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        category_id = request.POST.get('category')


        category = Category.objects.get(pk=category_id)

        product = Product.objects.create(name=name, description=description, price=price, stock=stock, image=image, image2=image2, image3=image3, category=category)

        

        product.save()


        return redirect('admin_products')


    return render(request,'adding_admin_products.html',context)



def admin_order_list(request):
    orders = Order.objects.all()
    return render(request, 'admin_order_list.html', {'orders': orders})






@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            return redirect('admin_order_list')
        else:
            return HttpResponseForbidden("Invalid status")

    return redirect('admin_order_list')



@login_required
def order_details_admin(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_details_admin.html', {'order': order})



@login_required
def add_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_amount = request.POST.get('discount_amount')
        min_order_amount = request.POST.get('min_order_amount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')

        valid_from = datetime.strptime(valid_from, '%Y-%m-%d').date()
        valid_to = datetime.strptime(valid_to, '%Y-%m-%d').date()

        Coupon.objects.create(
            code=code,
            discount_amount=discount_amount,
            min_order_amount=min_order_amount,
            valid_from=valid_from,
            valid_to=valid_to
        )

        return redirect('coupon_manage')  # Update this with the actual URL name for managing coupons

    return render(request, 'add_coupon.html')


@login_required
def coupon_manage(request):
    coupons = Coupon.objects.all()
    return render(request, 'coupon_manage.html', {'coupons': coupons})




@login_required
def deactivate_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.active = False
    coupon.save()
    messages.success(request, f'Coupon {coupon.code} has been deactivated.')
    return redirect('coupon_manage')


@login_required
def activate_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.active = True
    coupon.save()
    messages.success(request, f'Coupon {coupon.code} has been activated.')
    return redirect('coupon_manage')



@login_required(login_url='/login/')
def generatePdf(request):
    today = timezone.now()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    period = request.GET.get('period', 'month')

    if start_date_str and end_date_str:
        # Custom date range provided
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        # Use predefined period
        if period == 'day':
            start_date = today - timezone.timedelta(days=1)
        elif period == 'week':
            start_date = today - timezone.timedelta(weeks=1)
        elif period == 'month':
            start_date = today - timezone.timedelta(days=30)
        elif period == 'year':
            start_date = today - timezone.timedelta(days=365)
        else:
            return render(request, 'invalid_period.html')

        end_date = today
    
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    
    total_sales_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    # total_discount_amount = orders.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    
    p = canvas.Canvas(response)
    
    # Add information to the PDF
    p.drawString(100, 800, f"Total Sales Count: {total_sales_count}")
    p.drawString(100, 780, f"Total Sales Amount: {total_sales_amount}")
    # p.drawString(100, 760, f"Total Discount Amount: {total_discount_amount}")
    p.drawString(100, 740, f"Period: {period.capitalize()}")

    # Save the PDF
    p.showPage()
    p.save()

    return response