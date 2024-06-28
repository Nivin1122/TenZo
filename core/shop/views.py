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
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle,Spacer





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

    selected_category = None
    category_id = request.GET.get('category')
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            products_list = products_list.filter(category=selected_category)
        except Category.DoesNotExist:
            selected_category = None

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
        'sort_by': sort_by,
        'selected_category': selected_category
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
            
            Wishlist.objects.filter(user=user, product=product).delete()
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
    total_price = sum(item.product.get_discounted_price() * item.quantity for item in cart_items)
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

        total_price = sum(item.product.get_discounted_price() * item.quantity for item in cart_items)

        if payment_method == 'COD' and total_price > 1000:
            messages.error(request, "Cash on Delivery is not available for orders above 1000 Rs. Please choose another payment method.")
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
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})




@login_required
def cancel_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    
    if order.status != 'Canceled' and order.payment_method == 'COD':
      
        if order.status == 'Delivered':
            try:
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance += order.total_price
                wallet.save()
            except Wallet.DoesNotExist:
                pass
    if order.payment_method == "RAZORPAY":
        if order.status != 'Canceled':
            order.status = 'Canceled'
            order.save()

            wallet = Wallet.objects.get(user=request.user)
            wallet.balance += order.total_price
            wallet.save()

        
    order.status = 'Canceled'
    order.save()
    return redirect('list_orders')







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
    



@login_required(login_url='/login/')
def generatePdf(request, order_id):
    # Retrieve the order object
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    company_name = Paragraph("TenZo", styles['Title'])
    elements.append(company_name)
    elements.append(Spacer(1, 12))

    # Title
    title = Paragraph("Invoice", styles['Title'])
    elements.append(title)

    # Create the main table data
    main_table_data = []

    # Order Info
    order_info_data = [
        ["Order ID:", str(order.id)],
        ["Date:", order.created_at.strftime("%Y-%m-%d %H:%M")]
    ]
    main_table_data.append([Table(order_info_data, colWidths=[100, 300], style=[
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
    ])])

    # Add space between sections
    main_table_data.append([""])

    # Shipping Address
    shipping_info_data = [
        ["Shipping Address:"],
        [f"Name: {order.shipping_address.name}"],
        [f"Street: {order.shipping_address.street}"],
        [f"City: {order.shipping_address.city}"],
        [f"State: {order.shipping_address.state}"],
        [f"Country: {order.shipping_address.country}"],
        [f"Phone: {order.shipping_address.phone_no}"]
    ]
    main_table_data.append([Table(shipping_info_data, colWidths=[400], style=[
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey)
    ])])

    # Add space between sections
    main_table_data.append([""])

    # Order Items
    order_items_data = [
        ["Product", "Quantity", "Price"]
    ]
    for item in order.items.all():
        product_name = item.product.name
        quantity = str(item.quantity)
        price = f"Rs.{item.product.get_discounted_price() * item.quantity:.2f}"
        order_items_data.append([product_name, quantity, price])

    order_items_table = Table(order_items_data, colWidths=[250, 75, 75], style=[
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ])
    main_table_data.append([order_items_table])

    # Add space between sections
    main_table_data.append([""])

    # Total Price
    total_price_data = [
        ["Total Price:", f"Rs.{order.total_price:.2f}"]
    ]
    main_table_data.append([Table(total_price_data, colWidths=[300, 100], style=[
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey)
    ])])

    # Create the main table
    main_table = Table(main_table_data, colWidths=[410], style=[
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])
    elements.append(main_table)

    doc.build(elements)

    # Get PDF content and close buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Write PDF response
    response.write(pdf)

    return response