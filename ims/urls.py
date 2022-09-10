from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('update_cart/', views.updateCart, name='update_cart'),
    path('update_quantity/', views.updateQuantity, name='update_quantity'),
    path('cart/', views.cart, name='cart'),
    path('completed/', views.sale_complete, name='completed'),
    path('checkout/', views.checkout, name='checkout'),
    path('category/', views.category, name='category'),
    path('category_edit/<str:pk>/', views.update_category, name='category_edit'),
    path('category_delete/<str:pk>/', views.delete_category, name='category_delete'),
    path('product_details/<str:pk>/', views.product_detail, name='product_details'),
    path('product/', views.product, name='product'),
    path('productedit/<str:pk>/', views.productEdit, name='productedit'),
    path('product_delete/<str:pk>/', views.delete_product, name='product_delete'),
    path('sales/', views.sales, name='sales'),
    path('records/', views.report, name='records'),
    path('inventory/', views.inventory, name='inventory'),
    path('staff/', views.staffs, name='staff'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
]
