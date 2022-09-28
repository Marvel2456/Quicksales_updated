from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import *

class ProductForm(ModelForm):
    class Meta:
       model = Product
       fields = ('product_name', 'category', 'brand', 'cost_price', 'sale_price', 'unit', 'batch_no')
       
       widgets = {
           'category': forms.Select(attrs={'class':'form-select', 'placeholder':'Category', 'required':True, 'title':'Select Category'})
       }
       

class EditProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'brand', 'cost_price', 'sale_price', 'unit', 'batch_no',)

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('category_name',)

class EditCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('category_name',)

# class RestockForm(ModelForm):
#     class Meta:
#         model = Product
#         fields = ('quantity_restocked', 'sale_price', 'cost_price')
