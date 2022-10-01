from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from .models import Category, Product, Sale, SalesItem, Inventory
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from . forms import EditInventoryForm, ProductForm, EditProductForm, CategoryForm, EditCategoryForm, CreateInventoryForm, RestockForm
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

def category_list(request):
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
        return redirect('products')
    context = {
        'category':category
    }
    return render(request, 'ims/category_delete.html', context)

def store(request):
    inventory = Inventory.objects.all()

    context = {
        'inventory':inventory
    }
    return render(request, 'ims/store.html', context)

def delete_product(request, pk):
    product = Product.objects.get(id = pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Succesfully deleted")
        return redirect('products')
    context = {
        'product':product
    }
    return render(request, 'ims/product_delete.html', context)

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
    inventory = Inventory.objects.all()
    sale, created = Sale.objects.get(id=pk, completed=True)
    saleItem, created = SalesItem.objects.get(sale=sale, inventory=inventory)

    context = {
        'saleItem':saleItem
    }
    return render(request, 'ims/reciept.html', context)


def product_category(request):
    products = Product.objects.all().order_by('-date_created')
    category = Category.objects.filter().all()
    form = ProductForm()
    catform = CategoryForm()
    if request.method == "POST":
        catform = CategoryForm(request.POST)
        if catform.is_valid():
            catform.save()
            messages.success(request, 'successfully created')
            return redirect('products')
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('products')
        
    context = {
        'catform':catform,
        'category':category,
        'form':form,
        'products':products
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
                return redirect('products')

def inventory_list(request):
    inventory = Inventory.objects.all()
    product = Product.objects.filter().all()
    form = CreateInventoryForm
    if request.method == "POST":
        form = CreateInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'successfully created')
            return redirect('inventory')

    context = {
        'inventory':inventory,
        'product':product,
        'form':form
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
                form.save()
                messages.success(request, 'successfully updated')
                return redirect('inventorys')

def staffs(request):
    return render(request, 'ims/staff.html')