from django.contrib import admin
from .models import Product, Sale, SalesItem, Category, Inventory, PaymentMethod, Supplier, ErrorTicket

# Register your models here.
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SalesItem)
admin.site.register(Category)
admin.site.register(Inventory)
admin.site.register(PaymentMethod)
admin.site.register(Supplier)
admin.site.register(ErrorTicket)