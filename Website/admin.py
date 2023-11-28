from django.contrib import admin

# Register your models here.
from Website.models import Blog
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'date', 'author', 'image']
    search_fields = ['title', 'content', 'date', 'author', 'image']

from Website.models import Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'image', 'icon']
    search_fields = ['title', 'description', 'image', 'icon']

