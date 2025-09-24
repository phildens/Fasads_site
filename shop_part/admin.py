# shop_part/admin.py
from django.contrib import admin
from django import forms

from .models import Product, FilterKey, Category  # Product остаётся в «Интернет-магазин»
from .proxies import (
    # характеристики
    CategoryChar, TypeMaterialChar, FormatChar, ColorChar, FrosenDefenderChar,
    ManufactorChar, StrengthGradeChar, WaterResistanceChar, EmptinessChar, ProductTypeChar,
    # галерея
    GalleryProxy, BigGaleryProxy, SmallGalleryProxy
)
from .models import Questions, ContactRequest  # куда хотите, можно оставить в «Интернет-магазин»


# ====== ТОВАРЫ (Интернет-магазин) ======
class GalleryInline(admin.TabularInline):
    model = GalleryProxy            # используем прокси, работает как и раньше
    fk_name = 'product'
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [GalleryInline]
    list_display = ('name', 'card_image', 'type_material', 'description')
    search_fields = ('name', 'type_material__name', 'description')
    list_filter = ('type_material', 'manufacturer', 'product_type')


# ====== ХАРАКТЕРИСТИКИ ======
@admin.register(CategoryChar)
class CategoryCharAdmin(admin.ModelAdmin):
    # форма с чекбоксами для filters_enabled (как было)
    class _Form(forms.ModelForm):
        filters_enabled = forms.MultipleChoiceField(
            required=False,
            choices=[(c.value, c.label) for c in FilterKey],
            widget=forms.CheckboxSelectMultiple
        )
        class Meta:
            model = Category
            fields = "__all__"
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.fields["filters_enabled"].initial = (self.instance.filters_enabled or [])
        def clean_filters_enabled(self):
            return self.cleaned_data["filters_enabled"] or []

    form = _Form
    list_display = ("id", "name", "link_name")
    search_fields = ("name", "link_name")

@admin.register(TypeMaterialChar)
class TypeMaterialCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(FormatChar)
class FormatCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ColorChar)
class ColorCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(FrosenDefenderChar)
class FrosenDefenderCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(StrengthGradeChar)
class StrengthGradeCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(WaterResistanceChar)
class WaterResistanceCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ManufactorChar)
class ManufactorCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(EmptinessChar)
class EmptinessCharAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductTypeChar)
class ProductTypeCharAdmin(admin.ModelAdmin):
    list_display = ('name',)


# ====== ГАЛЕРЕЯ ======
class SmallGalleryInline(admin.TabularInline):
    model = SmallGalleryProxy
    fk_name = 'object'
    extra = 0

@admin.register(BigGaleryProxy)
class BigGaleryProxyAdmin(admin.ModelAdmin):
    inlines = [SmallGalleryInline]
    list_display = ('position', 'name', 'product', 'our_supplies')

@admin.register(GalleryProxy)
class GalleryProxyAdmin(admin.ModelAdmin):
    list_display = ('product',)

# (опционально) если нужна отдельная админка для фото объекта
@admin.register(SmallGalleryProxy)
class SmallGalleryProxyAdmin(admin.ModelAdmin):
    list_display = ('object',)


# ====== Прочее (куда оставите — ваш выбор) ======
@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "description")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
