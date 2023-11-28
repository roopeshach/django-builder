from django.contrib import admin

# Register your models here.
from Restaurant.models import Waiter
@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'address']
    search_fields = ['name', 'email', 'address']

from Restaurant.models import Cook
@admin.register(Cook)
class CookAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    search_fields = ['name', 'email']

