from django.shortcuts import render,redirect
from product_side.models import Product,Category,Cart,CartItem
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from user_side.models import Address



# Create your views here.
def index(request):
    
    products = Product.objects.filter(is_listed=True)

    context = {
        'products' : products
    }
    return render(request, 'index.html',context)



def all_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(is_listed=True)
    categories = Category.objects.filter(is_listed=True)
 
    if query:
        products = products.filter(
            Q(name__icontains=query)
        )

    sort_by = request.GET.get('sortby')
    if sort_by == 'low_to_high':
        products = Product.objects.filter(is_listed=True).order_by('price')
    elif sort_by == 'high_to_low':
        products = Product.objects.filter(is_listed=True).order_by('-price')

    else:
        products = Product.objects.filter(is_listed=True)


    context = {
        'products': products, 
        'categories': categories,
        'query' : query,
        'sort_by': sort_by
    }
    return render(request, 'all_products.html', context)



def product_details(request, id):

    products = get_object_or_404(Product, id=id)

    context = {'products': products}
    return render(request, 'product_details.html', context)




@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock > 0:
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)
            if not created:
                if cart_item.quantity < 5:
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, "Product added to cart.")
                else:
                    messages.error(request, "Maximum 5 products allowed per person.")
            else:
                cart_item.quantity = 1
                cart_item.save()
                messages.success(request, "Product added to cart.")
        else:
            messages.error(request, "Product is out of stock.")
        
    return redirect('cart')




def list_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price':total_price})



def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def checkout(request):
    user = request.user
    user_addresses = Address.objects.filter(user=request.user)
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'checkout.html',{'user_addresses':user_addresses, 'total_price' : total_price})