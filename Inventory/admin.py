from django.contrib import admin

# Register your models here.
from Inventory.models import Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image', 'added_on', 'description', 'category']
    search_fields = ['name', 'price', 'image', 'added_on', 'description', 'category']

from Inventory.models import ProductCategory
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'added_on']
    search_fields = ['name', 'description', 'added_on']

