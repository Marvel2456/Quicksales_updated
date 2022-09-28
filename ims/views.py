from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from .models import Category, Product, Sale, SalesItem
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from . forms import ProductForm, EditProductForm, CategoryForm, EditCategoryForm
from django.http import JsonResponse
import json
# import datetime

# Create your views here

@unauthenticated_user
def loginUser(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Username or Password is not correct')

    return render(request, 'ims/login.html')


        
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url=('login'))
def dashboard(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    products = Product.objects.all()
    category = Category.objects.all()
    
    total_product = products.count()
    total_category = category.count()
    transaction = len(Sale.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sale.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('final_total_price',flat=True))
    context = {
        'products':products,
        'category':category,
        'total_product':total_product,
        'total_category':total_category,
        'transaction':transaction,
        'total_sales':total_sales
    }
    return render(request, 'ims/index.html', context)

def category(request):
    category = Category.objects.all()
    
    context = {
        'category':category,
    }
    return render(request, 'ims/category.html', context)

def delete_category(request, pk):
    category = Category.objects.get(id = pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Succesfully deleted")
        return redirect('inventory')
    context = {
        'category':category
    }
    return render(request, 'ims/category_delete.html', context)

def update_category(request, pk):
    category = Category.objects.get(id=pk)
    form = EditCategoryForm(instance=category)
    if request.method == 'POST':
        form = EditCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('inventory')
    context = {
        'category':category,
        'form':form
    }
    return render(request, 'ims/category_edit.html', context)

def product(request):
    product = Product.objects.all()

    context = {
        
        'product':product,
    }
    return render(request, 'ims/product.html', context)


def product_detail(request, pk):
    product = Product.objects.get( id=pk )
    # form = RestockForm()
    # if request.method == "POST":
    #     form = RestockForm(request.POST, instance=product)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, "Successfully updated")
    #         return redirect('product_details', pk=product.id)
    
    
    context = {
        # 'form':form,
        'product':product,
    }

    return render(request, 'ims/product_details.html', context)

def delete_product(request, pk):
    product = Product.objects.get(id = pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Succesfully deleted")
        return redirect('inventory')
    context = {
        'product':product
    }
    return render(request, 'ims/product_delete.html', context)

def cart(request):
    product = Product.objects.all()
    
    if request.user.is_authenticated:
        staff = request.user.staff
        sale , created = Sale.objects.get_or_create(staff=staff, completed=False)
        items = sale.salesitem_set.all()
        
    context = {
        'items':items,
        'sale':sale,
        'product':product
    }
    return render(request, 'ims/cart.html', context)

def checkout(request):
    product = Product.objects.all()
    
    if request.user.is_authenticated:
        staff = request.user.staff
        sale , created = Sale.objects.get_or_create(staff=staff, completed=False)
        items = sale.salesitem_set.all()
        
    context = {
        'items':items,
        'sale':sale,
        'product':product
    }
    return render(request, 'ims/checkout.html', context)

def updateCart(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Product:', productId)
    print('Action:', action)

    staff = request.user.staff
    product = Product.objects.get(id=productId)
    sale, created = Sale.objects.get_or_create(staff=staff, completed=False)
    saleItem, created = SalesItem.objects.get_or_create(sale=sale, product=product)

    if action == 'add':
        saleItem.quantity = (saleItem.quantity + 1)
    saleItem.save()

    if saleItem.quantity <= 0:
        saleItem.delete()

    context = {
        'qty': sale.get_cart_items
    }

    return JsonResponse(context, safe=False)

def updateQuantity(request):
    data = json.loads(request.body)
    input_value = int(data['val'])
    product_Id = data['prod_id']
    
    staff = request.user.staff
    product = Product.objects.get(id=product_Id)
    sale, created = Sale.objects.get_or_create(staff=staff, completed=False)
    saleItem, created = SalesItem.objects.get_or_create(sale=sale, product=product)
    saleItem.quantity = input_value
    saleItem.save()

    if saleItem.quantity <= 0:
        saleItem.delete()

    context = {
        'sub_total':saleItem.get_total,
        'final_total':sale.get_cart_total,
        'total_quantity':sale.get_cart_items
    }

    return JsonResponse(context, safe=False)

def sale_complete(request):
    transaction_id = datetime.now().timestamp()
    data = json.loads(request.body)
    staff = request.user.staff
    sale, created = Sale.objects.get_or_create(staff=staff, completed=False)
    sale.transaction_id = transaction_id
    total = float(data['payment']['total_cart'])
    sale.final_total_price = sale.get_cart_total

    if total == sale.get_cart_total:
        sale.completed = True
    sale.save()

    return JsonResponse('Payment completed', safe=False)

def sales(request):
    sale = Sale.objects.all()

    context = {
        'sale':sale,
    }
    return render(request, 'ims/sales.html', context)
def sale_delete(request, pk):
    sale = Sale.objects.get(id=pk)
    if request.method == "POST":
        sale.delete()
        messages.success(request, "Succesfully deleted")
        return redirect('sales')
    context = {
        'sale':sale
    }
    return render(request, 'ims/sales_delete.html', context)

def report(request):
    return render(request, 'ims/records.html')

def reciept(request, pk):
    
    product = Product.objects.all()
    sale, created = Sale.objects.get(id=pk, completed=True)
    saleItem, created = SalesItem.objects.get(sale=sale, product=product)

    context = {
        'saleItem':saleItem
    }
    return render(request, 'ims/reciept.html', context)


def inventory(request):
    products = Product.objects.all().order_by('-date_created')
    category = Category.objects.all()
    form = ProductForm()
    catform = CategoryForm()
    if request.method == "POST":
        catform = CategoryForm(request.POST)
        if catform.is_valid():
            catform.save()
            messages.success(request, 'successfully created')
            return redirect('inventory')
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('inventory')
        
    context = {
        'catform':catform,
        'category':category,
        'form':form,
        'products':products
    }
    return render(request, 'ims/inventory.html', context)
        
def productEdit(request, pk):
    product = Product.objects.get(id=pk)
    form = EditProductForm(instance=product)
    if request.method == 'POST':
        form = EditProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('productedit',pk=product.id)
    
    context = {
        'form':form,
        'product':product
    }
    return render(request, 'ims/productedit.html', context)

def staffs(request):
    return render(request, 'ims/staff.html')