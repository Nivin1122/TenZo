from django.shortcuts import render,redirect
from product_side.models import Product,Category,Cart,CartItem,Order,OrderItem
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from user_side.models import Address
from django.utils import timezone



# Create your views here.
def index(request):
    
    products = Product.objects.filter(is_listed=True)

    context = {
        'products' : products
    }
    return render(request, 'index.html',context)



@login_required
def all_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(is_listed=True, stock__gt=0) 
    categories = Category.objects.filter(is_listed=True)

    if query:
        products = products.filter(Q(name__icontains=query))

    sort_by = request.GET.get('sortby')
    if sort_by == 'low_to_high':
        products = products.order_by('price')
    elif sort_by == 'high_to_low':
        products = products.order_by('-price')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock,
                    'image_url': product.image.url,
                    'category': product.category.name,
                }
                for product in products
            ]
        }
        return JsonResponse(response_data)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
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
        response_data = {}
        
        if product.stock > 0:
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)
            if not created:
                if cart_item.quantity < product.stock:
                    cart_item.quantity += 1
                    cart_item.save()
                    response_data['message'] = "Product added to cart."
                    response_data['success'] = True
                else:
                    response_data['message'] = "No more products left."
                    response_data['success'] = False
            else:
                cart_item.quantity = 1
                cart_item.save()
                response_data['message'] = "Product added to cart."
                response_data['success'] = True
        else:
            response_data['message'] = "Product is out of stock."
            response_data['success'] = False
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(response_data)
        else:
            if response_data['success']:
                messages.success(request, response_data['message'])
            else:
                messages.error(request, response_data['message'])
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



@login_required
def place_order(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if not selected_address_id:
            return redirect('checkout') 

        address = Address.objects.get(id=selected_address_id)
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        
        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method='COD',
            total_price=total_price,
            created_at=timezone.now(),
            status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
  
            item.product.stock -= item.quantity
            item.product.save()


        cart_items.delete()

        return redirect('order_success', order_id=order.id)

    return redirect('checkout')



def order_success(request, order_id):
    return render(request, 'order_success.html', {'order_id': order_id})



@login_required
def list_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'list_orders.html', {'orders': orders})



@login_required
def cancel_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # if request.method == 'POST':
    order.delete()
    return redirect('list_orders')
# return render(request, 'list_orders.html', {'order': order})