from django.contrib import admin

from shop_part.models import Product, TypeMaterial, Category, Format, Color, FrosenDefender, Manufactor, StrengthGrade, \
    WaterResistance, Emptiness, Questions, ProductType, Gallery


# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [GalleryInline, ]
    list_display = ('name', 'card_image', 'type_material', 'description')
    search_fields = ('name', 'type_material', 'description')
    list_filter = ('name', 'type_material', 'description')


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(TypeMaterial)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(FrosenDefender)
class FrosenDefenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Manufactor)
class ManufactorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(StrengthGrade)
class StrengthGradeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(WaterResistance)
class WaterResistanceAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Emptiness)
class EmptinessAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

from .models import ContactRequest

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "description")
    list_filter   = ("created_at",)
    readonly_fields = ("created_at",)
