from django.contrib import admin

from shop_part.models import Product


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', )
    search_fields = ('name', 'price')
    list_filter = ('name', 'price')