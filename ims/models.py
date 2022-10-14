from datetime import date
from enum import unique
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Staff(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    category_name = models.CharField(max_length=200, unique=True)
    last_updated = models.DateField(auto_now=True,)
    date_created = models.DateTimeField(auto_now_add=True,)

    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=150, blank=True, null=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=150, blank=True, null=True)
    product_code = models.CharField(max_length=100)
    batch_no = models.CharField(max_length=20, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateField(auto_now=True,)
    date_created = models.DateTimeField(auto_now_add=True,)
    profit = models.FloatField(blank=True, null=True)
    # history = HistoricalRecords()
    
    def __str__(self):
        return self.product_name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    quantity_available = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0, blank=True, null=False)
    choices = (
        ('Available', 'Item is currently available'),
        ('Restocking', 'Currently out of stock'),
    )
    status = models.CharField(max_length=20, choices=choices, default="Available", blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    sale_price = models.FloatField(blank=True, null=True)
    quantity_restocked = models.IntegerField(default=0, blank=True, null=True)
    count = models.IntegerField(default=0, blank=True, null=True)
    store = models.IntegerField(default=0)
    variance = models.IntegerField(default=0)
    last_updated = models.DateField(auto_now=True,)
    date_created = models.DateTimeField(auto_now_add=True,)

    class Meta:
        verbose_name_plural = "inventories"

    def __str__(self):
        return self.product.product_name

    @property
    def store_quantity(self):
        salesitem = self.salesitem_set.all()
        store = self.quantity - sum([item.quantity for item in salesitem])
        return store

    @property
    def quantity_sold(self):
        salesitem = self.salesitem_set.all()
        sold = sum([item.quantity for item in salesitem])
        return sold

    # @property
    # def quantity_sold_date(self):
    #     salesitem = self.salesitem_set.all()
    #     date_sold = [item.last_updated for item in salesitem]
    #     return date_sold
    
class Sale(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, blank=True, null=True)
    choices = (
        ('General', 'General'),
        ('Promo', 'Promo'),
    )
    mode_of_sales = models.CharField(max_length=50, choices=choices,default="General", blank=True, null=True)
    total_profit = models.FloatField(default=0, blank=True, null=True)
    final_total_price = models.FloatField(default=0, blank=True, null=True)
    discount =  models.FloatField(default=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.transaction_id)

    @property
    def get_cart_total(self):
        salesitem = self.salesitem_set.all()
        total = sum([item.get_total for item in salesitem])
        return total

    @property
    def get_cart_items(self):
        salesitem = self.salesitem_set.all()
        total = sum([item.quantity for item in salesitem])
        return total

    @property
    def get_total_profit(self):
        salesitem = self.salesitem_set.all()
        profit = sum([item.get_profit for item in salesitem])
        return profit
        # display daily profits on the dashboard and on the sales page

class SalesItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, blank=True, null=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, blank=True, null=True)
    total = models.FloatField(default=0)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return str(self.inventory)
    
    @property
    def get_total(self):
        total = self.inventory.sale_price * self.quantity
        return total

    @property
    def get_profit(self):
        profit = self.inventory.sale_price - self.inventory.cost_price
        return profit