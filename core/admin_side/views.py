from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from user_side.models import Customuser
from product_side.models import Category,Product,Order,Offer,Coupon,OrderItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum,Count
from datetime import datetime
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from openpyxl import Workbook
import json




# Create your views here.
def admin_home(request):
    overall_sales_count = Order.objects.aggregate(total_sales=Count('total_price'))['total_sales'] or 0
    overall_order_amount = Order.objects.aggregate(total_order_amount=Sum('total_price'))['total_order_amount'] or 0

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
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    # Calculate overall discount
    total_discount_amount = sum(
        item.quantity * (item.product.price - item.product.get_discounted_price())
        for order in orders
        for item in order.items.all()
    )

    # Prepare data for the sales chart
    sales_by_date = orders.extra({'date': 'date(created_at)'}).values('date').annotate(total_sales=Sum('total_price')).order_by('date')
    dates = [entry['date'].strftime('%Y-%m-%d') for entry in sales_by_date]
    sales = [float(entry['total_sales']) for entry in sales_by_date]

    # Prepare data for the donut chart
    top_products = OrderItem.objects.values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    product_names = [product['product__name'] for product in top_products]
    product_quantities = [product['total_quantity'] for product in top_products]

    context = {
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_sales_amount': total_sales_amount,
        'total_discount_amount': total_discount_amount,
        'total_sales_count': total_sales_count,
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
        'dates': json.dumps(dates),
        'sales': json.dumps(sales),
        'product_names': json.dumps(product_names),
        'product_quantities': json.dumps(product_quantities),
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

        return redirect('coupon_manage')  

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
    start_date_str = request.GET.get('start_date', '').strip()
    end_date_str = request.GET.get('end_date', '').strip()
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
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    
    # Adding shop name in bold letters
    shop_name_style = styles['Title']
    shop_name = Paragraph("TenZo", shop_name_style)
    elements.append(shop_name)
    
    title = Paragraph("Sales Report", styles['Title'])
    elements.append(title)

    summary_data = [
        ["Total Sales Count", total_sales_count],
        ["Total Sales Amount", f"{total_sales_amount:.2f}"],
        ["Period", period.capitalize()]
    ]

    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)

    elements.append(Paragraph("Sales History:", styles['Heading2']))

    data = [["Order ID", "Date", "Product Name", "Total Price", "Discount Amount"]]
    for order in orders:
        for item in order.items.all():  # Accessing related OrderItems
            data.append([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                item.product.name,
                f"{item.product.get_discounted_price() * item.quantity:.2f}",  # Total Price formatted to 2 decimals
                f"{item.product.price - item.product.get_discounted_price():.2f}"  # Discount Amount formatted to 2 decimals
            ])

    table = Table(data, colWidths=[1.5 * inch] * 5)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)

    return response




@login_required(login_url='/login/')
def generateExcel(request):
    today = timezone.now()
    start_date_str = request.GET.get('start_date', '').strip()
    end_date_str = request.GET.get('end_date', '').strip()
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

    # Compute total sales amount
    total_sales_amount = sum(order.total_price for order in orders)

    # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    # Adding headers
    ws.append(["Order ID", "Date", "Total Price"])

    # Adding data
    for order in orders:
        ws.append([order.id, order.created_at.strftime("%Y-%m-%d %H:%M"), order.total_price])

    # Adding total sales amount row
    ws.append(["Total Sales Amount", total_sales_amount])

    # Create a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'

    # Save workbook to response
    wb.save(response)

    return response




def admin_offers(request):
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
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    offers = Offer.objects.filter(active=True)

    context = {
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_sales_amount': total_sales_amount,
        'total_sales_count': total_sales_count,
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
        'offers': offers,
    }

    return render(request, 'admin_offers.html', context)



def add_offer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        discount_percentage = request.POST.get('discount_percentage')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        active = request.POST.get('active') == 'True'

        
        valid_from = timezone.make_aware(timezone.datetime.strptime(valid_from, '%Y-%m-%dT%H:%M'))
        valid_to = timezone.make_aware(timezone.datetime.strptime(valid_to, '%Y-%m-%dT%H:%M'))

    
        offer = Offer(name=name, discount_percentage=discount_percentage, valid_from=valid_from, valid_to=valid_to, active=active)
        offer.save()

        messages.success(request, 'Offer added successfully!')
        return redirect('admin_offers') 
    return render(request, 'add_offer.html')



@login_required(login_url='/login/')
def assign_offer_to_product(request):
    if not request.user.is_superuser:
        return redirect('admin_home')

    if request.method == 'POST':
        product_id = request.POST.get('product')
        offer_id = request.POST.get('offer')
        
        try:
            product = Product.objects.get(id=product_id)
            offer = Offer.objects.get(id=offer_id)
            product.offer = offer
            product.save()
            return redirect('admin_offers')
        except Product.DoesNotExist:
        
            pass
        except Offer.DoesNotExist:
       
            pass
    
    products = Product.objects.all()
    offers = Offer.objects.filter(active=True)
    
    return render(request, 'assign_offer_to_product.html', {
        'products': products,
        'offers': offers
    })