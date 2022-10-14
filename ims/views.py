from turtle import title
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from .models import Category, Product, Sale, SalesItem, Inventory
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from . forms import EditInventoryForm, ProductForm, EditProductForm, CategoryForm, EditCategoryForm, CreateInventoryForm, RestockForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Max
# from django_pandas.io import read_frame
# import plotly
# import plotly.express as px
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
    today_profit = Sale.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_profits = sum(today_profit.values_list('total_profit', flat=True))
    sale = Sale.objects.all()




    context = {
        'products':products,
        'category':category,
        'total_product':total_product,
        'total_category':total_category,
        'transaction':transaction,
        'total_sales':total_sales,
        'total_profits':total_profits,
        'sale':sale
        # 'sale_graph':sale_graph,
    }
    return render(request, 'ims/index.html', context)

def store(request):
    inventory = Inventory.objects.all()
    paginator = Paginator(Inventory.objects.all(), 3)
    page = request.GET.get('page')
    inventory_page = paginator.get_page(page)
    nums = "a" *inventory_page.paginator.num_pages
    product_contains_query = request.GET.get('product')

    if product_contains_query != '' and product_contains_query is not None:
        inventory_page = inventory.filter(product__product_name__icontains=product_contains_query)


    context = {
        'inventory':inventory,
        'inventory_page':inventory_page,
        'nums':nums
    }
    return render(request, 'ims/store.html', context)

def cart(request):
    inventory = Inventory.objects.all()
    
    if request.user.is_authenticated:
        staff = request.user.staff
        sale , created = Sale.objects.get_or_create(staff=staff, completed=False)
        items = sale.salesitem_set.all()
        
    context = {
        'items':items,
        'sale':sale,
        'inventory':inventory
    }
    return render(request, 'ims/cart.html', context)

def checkout(request):
    inventory = Inventory.objects.all()
    
    if request.user.is_authenticated:
        staff = request.user.staff
        sale , created = Sale.objects.get_or_create(staff=staff, completed=False)
        items = sale.salesitem_set.all()
        
    context = {
        'items':items,
        'sale':sale,
        'inventory':inventory
    }
    return render(request, 'ims/checkout.html', context)

def updateCart(request):
    data = json.loads(request.body)
    inventoryId = data['inventoryId']
    action = data['action']
    print('inventory:', inventoryId)
    print('Action:', action)

    staff = request.user.staff
    inventory = Inventory.objects.get(id=inventoryId)
    sale, created = Sale.objects.get_or_create(staff=staff, completed=False)
    saleItem, created = SalesItem.objects.get_or_create(sale=sale, inventory=inventory)

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
    inventory_Id = data['invent_id']
    
    staff = request.user.staff
    inventory = Inventory.objects.get(id=inventory_Id)
    sale, created = Sale.objects.get_or_create(staff=staff, completed=False)
    saleItem, created = SalesItem.objects.get_or_create(sale=sale, inventory=inventory)
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
    sale.total_profit = sale.get_total_profit

    if total == sale.get_cart_total:
        sale.completed = True   
    sale.save()   

    return JsonResponse('Payment completed', safe=False)

def sales(request):
    sale = Sale.objects.all()
    paginator = Paginator(Sale.objects.all(), 10)
    page = request.GET.get('page')
    sale_page = paginator.get_page(page)
    nums = "a" *sale_page.paginator.num_pages
    start_date_contains = request.GET.get('start_date')
    end_date_contains = request.GET.get('end_date')

    if start_date_contains != '' and start_date_contains is not None:
        sale_page = sale.filter(date_updated__gte=start_date_contains)

    if end_date_contains != '' and end_date_contains is not None:
        sale_page = sale.filter(date_updated__lte=end_date_contains)

    context = {
        'sale':sale,
        'sale_page':sale_page,
        'nums':nums
    }
    return render(request, 'ims/sales.html', context)

def sale(request, pk):
    sale = Sale.objects.get(id=pk)

    context = {
        'sale':sale
    }
    return render(request, 'ims/sales_delete.html', context)

def sale_delete(request):
    if request.method == 'POST':
        sale = Sale.objects.get(id = request.POST.get('id'))
        if sale != None:
            sale.delete()
            messages.success(request, "Succesfully deleted")
            return redirect('sales')
    

def report(request):
    return render(request, 'ims/records.html')

def reciept(request, pk):
    sale = Sale.objects.get(id = pk)
    salesitem = SalesItem.objects.filter(sale_id=sale).all()
    
    context = {
        'salesitem':salesitem,
        'sale':sale
    }
    return render(request, 'ims/reciept.html', context)

def product_category(request):
    products = Product.objects.all().order_by('-date_created')
    category = Category.objects.filter().all()
    paginator = Paginator(Product.objects.all(), 3)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    nums = "a" *products_page.paginator.num_pages
    product_contains = request.GET.get('product_name')
    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('products')

    if product_contains != '' and product_contains is not None:
        products_page = products.filter(product_name__icontains=product_contains)
        
    context = {
        'category':category,
        'form':form,
        'products':products,
        'products_page':products_page,
        'nums':nums
    }
    return render(request, 'ims/products.html', context)

def product(request, pk):
    products = Product.objects.get(id=pk)

    context = {
        'products':products
    } 
    return render(request, 'ims/modal_edit_product.html', context)

def edit_product(request):
    if request.method == 'POST':
        product = Product.objects.get(id = request.POST.get('id'))
        if product != None:
            form = EditProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'successfully updated')
                return redirect('products')

def delete_product(request):
    if request.method == 'POST':
        product = Product.objects.get(id = request.POST.get('id'))
        if product != None:
            product.delete()
            messages.success(request, "Succesfully deleted")
            return redirect('products')

def category_list(request):
    category = Category.objects.all()
    paginator = Paginator(Category.objects.all(), 3)
    page = request.GET.get('page')
    category_page = paginator.get_page(page)
    nums = "a" *category_page.paginator.num_pages
    category_contains = request.GET.get('category_name')
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('category_list')
            
    if category_contains != '' and category_contains is not None:
        category_page = category.filter(category_name__icontains=category_contains)

    context = {
        'category':category,
        'form':form,
        'category_page':category_page,
        'nums':nums
    }
    return render(request, 'ims/category.html', context)

def category(request, pk):
    category = Category.objects.get(id=pk)

    context = {
        'category':category
    }
    return render(request, 'ims/edit_category', context)

def edit_category(request):
    if request.method == 'POST':
        category = Category.objects.get(id = request.POST.get('id'))
        if category != None:
            form = EditCategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'successfully updated')
                return redirect('category_list')

def delete_category(request):
    if request.method == 'POST':
        category = Category.objects.get(id = request.POST.get('id'))
        if category != None:
            category.delete()
            messages.success(request, "Succesfully deleted")
            return redirect('category_list')

def inventory_list(request):
    inventory = Inventory.objects.all()
    product = Product.objects.filter().all()
    paginator = Paginator(Inventory.objects.all(), 3)
    page = request.GET.get('page')
    inventory_page = paginator.get_page(page)
    nums = "a" *inventory_page.paginator.num_pages
    product_contains_query = request.GET.get('product')
    form = CreateInventoryForm
    if request.method == "POST":
        form = CreateInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('inventorys')
    
    if product_contains_query != '' and product_contains_query is not None:
        inventory_page = inventory.filter(product__product_name__icontains=product_contains_query)

    context = {
        'inventory':inventory,
        'product':product,
        'form':form,
        'inventory_page':inventory_page,
        'nums':nums
    }
    return render(request, 'ims/inventory.html', context)

def inventory(request, pk):
    inventory = Inventory.objects.get(id=pk)

    context = {
        'inventory':inventory
    }
    return render(request, 'ims/edit_inventory.html', context)

def edit_inventory(request):
    if request.method == 'POST':
        inventory = Inventory.objects.get(id = request.POST.get('id'))
        if inventory != None:
            form = EditInventoryForm(request.POST, instance=inventory)
            if form.is_valid():
                form.save()
                messages.success(request, 'successfully updated')
                return redirect('inventorys')

def restock(request):
    if request.method == 'POST':
        inventory = Inventory.objects.get(id = request.POST.get('id'))
        if inventory != None:
            form = RestockForm(request.POST, instance=inventory)
            if form.is_valid():
                form.save(commit=False)
                inventory.quantity += inventory.quantity_restocked
                inventory.save()
                messages.success(request, 'successfully updated')
                return redirect('inventorys')

def delete_inventory(request):
    if request.method == 'POST':
        inventory = Inventory.objects.get(id = request.POST.get('id'))
        if inventory != None:
            inventory.delete()
            messages.success(request, "Succesfully deleted")
            return redirect('inventorys')

def staffs(request):
    return render(request, 'ims/staff.html')