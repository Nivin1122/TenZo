from django.shortcuts import render,redirect
from product_side.models import Product,Category,Cart,CartItem,Order,OrderItem,Coupon,Wishlist,Wallet,Shipping_address
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from user_side.models import Address
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal




# Create your views here.
def index(request):
    
    products = Product.objects.filter(is_listed=True).order_by('-id')

    context = {
        'products' : products
    }
    return render(request, 'index.html',context)




def all_products(request):
    query = request.GET.get('q')
    products_list = Product.objects.filter(is_listed=True, stock__gt=0)
    categories = Category.objects.filter(is_listed=True)

    if query:
        products_list = products_list.filter(Q(name__icontains=query))

    sort_by = request.GET.get('sortby')
    if sort_by == 'low_to_high':
        products_list = products_list.order_by('price')
    elif sort_by == 'high_to_low':
        products_list = products_list.order_by('-price')
    elif sort_by == 'Aa_to_Zz':
        products_list = products_list.order_by('name')
    elif sort_by == 'Zz_to_Aa':
        products_list = products_list.order_by('-name')

    paginator = Paginator(products_list, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

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



@login_required
def list_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.product.get_discounted_price() * item.quantity for item in cart_items)
    
    coupon_code = request.GET.get('coupon_code')
    discount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
            discount = coupon.discount_amount
            total_price -= discount
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code or coupon has expired.')

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'discount': discount})

# def list_cart(request):
#     user = request.user
#     cart_items = Cart.objects.filter(user=user)
#     total_price = sum(item.get_total_price() for item in cart_items)
#     return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



@login_required
def increase_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
        response = {
            'quantity': cart_item.quantity,
            'total_price': cart_item.quantity * cart_item.product.price,
            'cart_total': sum(item.quantity * item.product.price for item in Cart.objects.filter(user=request.user))
        }
    else:
        response = {'error': 'No more products left in stock.'}
    return JsonResponse(response)


@login_required
def decrease_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        response = {
            'quantity': cart_item.quantity,
            'total_price': cart_item.quantity * cart_item.product.price,
            'cart_total': sum(item.quantity * item.product.price for item in Cart.objects.filter(user=request.user))
        }
    else:
        response = {'error': 'Quantity cannot be less than 1.'}
    return JsonResponse(response)



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
        payment_method = request.POST.get('payment_method')
        if not selected_address_id:
            return redirect('checkout') 

        try:
            address = Address.objects.get(id=selected_address_id)
        except Address.DoesNotExist:
            return redirect('checkout')
        
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty. Please add at least one product to place an order.")
            return redirect('checkout') 

        shipping_address = Shipping_address.objects.create(
            street=address.street,
            city=address.city,
            state=address.state,
            zipcode=address.zipcode,
            country=address.country,
            user=request.user,
            name=address.name,
            phone_no=address.phone_no
        )

       
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            payment_method=payment_method,  
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


# @login_required
# def place_order(request):
#     if request.method == 'POST':
#         selected_address_id = request.POST.get('selected_address')
#         if not selected_address_id:
#             return redirect('checkout') 

#         address = Address.objects.get(id=selected_address_id)
#         cart_items = Cart.objects.filter(user=request.user)
#         total_price = sum(item.product.price * item.quantity for item in cart_items)
#         payment_method = Order
        
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             payment_method='COD',
#             total_price=total_price,
#             created_at=timezone.now(),
#             status='Pending'
#         )

#         for item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity
#             )
  
#             item.product.stock -= item.quantity
#             item.product.save()


#         cart_items.delete()

#         return redirect('order_success', order_id=order.id)

#     return redirect('checkout')



def order_success(request, order_id):
    return render(request, 'order_success.html', {'order_id': order_id})



@login_required
def list_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'list_orders.html', {'orders': orders})



@login_required
def cancel_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if the order is not already canceled and the payment method is COD
    if order.status != 'Canceled' and order.payment_method == 'COD':
        # Only add to wallet balance if the order is Delivered
        if order.status == 'Delivered':
            try:
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance += order.total_price
                wallet.save()
            except Wallet.DoesNotExist:
                # Handle if Wallet does not exist (though ideally, it should exist)
                pass
    if order.payment_method == "RAZORPAY":
        if order.status != 'Canceled':
            order.status = 'Canceled'
            order.save()

            wallet = Wallet.objects.get(user=request.user)
            wallet.balance += order.total_price
            wallet.save()

        
    # Mark the order as canceled regardless of payment method
    order.status = 'Canceled'
    order.save()
        
    return redirect('list_orders')



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})



@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, "wishlist.html", {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist')


@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Delivered':
        order.status = 'Returned'
        order.save()
        
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += Decimal(order.total_price)
        wallet.save()
        
    return redirect('list_orders')



# @login_required
# def wallet_detail(request):
#     wallet = get_object_or_404(Wallet, user=request.user)
#     return render(request, 'wallet_detail.html', {'wallet': wallet})

@login_required
def wallet_detail(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
        return render(request, 'wallet_detail.html', {'wallet': wallet})
    except Wallet.DoesNotExist:
        wallet_balance = Decimal('0.00')
        return render(request, 'wallet_detail.html', {'wallet_balance': wallet_balance})