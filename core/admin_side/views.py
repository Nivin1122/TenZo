from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from user_side.models import Customuser
from product_side.models import Category,Product,Order
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden



# Create your views here.
def admin_home(request):
    return render(request, 'admin_home.html')


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
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_details_admin.html', {'order': order})