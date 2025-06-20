from django.contrib import admin

from shop_part.models import Product, Type, Category


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_image', 'type','description')
    search_fields = ('name', 'type','description')
    list_filter = ('name', 'type','description')

@admin.register(Type)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
