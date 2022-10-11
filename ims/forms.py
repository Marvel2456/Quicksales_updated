from django.forms import ModelForm, ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import *

class ProductForm(ModelForm):
    class Meta:
       model = Product
       fields = ('product_name', 'category', 'brand', 'unit', 'batch_no')
       
       widgets = {
           'category': forms.Select(attrs={'class':'form-select', 'placeholder':'Category', 'required':True, 'title':'Select Category'})
       }

    def clean(self):
        super(ProductForm, self).clean()

        product_name = self.cleaned_data.get('product_name')
        category = self.cleaned_data.get('category')
        brand = self.cleaned_data.get('brand')
        unit = self.cleaned_data.get('unit')
        batch_no = self.cleaned_data.get('batch_no')

        if not product_name:
            self._errors['product_name'] = self.error_class([
                'This field is required'])
        if not category:
            self._errors['category'] = self.error_class([
                'This field is required'])
        if not brand:
            self._errors['brand'] = self.error_class([
                'This field is required'])
        if not unit:
            self._errors['unit'] = self.error_class([
                'This field is required'])
        if not batch_no:
            self._errors['batch_no'] = self.error_class([
                'This field is required'])

        for product in Product.objects.all():
            if product.product_name == product_name:
                self._errors['product_name'] = self.error_class([
                'This product already exists'])

        return self.cleaned_data   

class EditProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'category', 'brand', 'unit', 'batch_no',)

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('category_name',)

    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if not category_name:
            raise forms.ValidationError('This field is required')
        for category in Category.objects.all():
            if category.category_name == category_name:
                raise forms.ValidationError(category_name + 'already exists')

class EditCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('category_name',)

class CreateInventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('product', 'quantity', 'cost_price', 'sale_price', 'reorder_level')

class InventorySearchForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ('product',)

class ProductSearchForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name',)

class RestockForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('quantity_restocked', 'sale_price', 'cost_price')

class EditInventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('product', 'quantity', 'cost_price', 'sale_price', 'reorder_level')
