from django.contrib import admin
from django import forms
from .models import Category, FilterKey
from shop_part.models import Product, TypeMaterial, Category, Format, Color, FrosenDefender, Manufactor, StrengthGrade, \
    WaterResistance, Emptiness, Questions, ProductType, Gallery, BigGalery, SmallGallery


# Register your models here.
class SmallGalleryInline(admin.TabularInline):
    model = SmallGallery
    fk_name = 'object'


@admin.register(BigGalery)
class BigGaleryAdmin(admin.ModelAdmin):
    inlines = [SmallGalleryInline]


# Галерея объектов
class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery


# Товары
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


class CategoryAdminForm(forms.ModelForm):
    filters_enabled = forms.MultipleChoiceField(
        required=False,
        choices=[(c.value, c.label) for c in FilterKey],
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        val = self.instance.filters_enabled or []
        self.fields["filters_enabled"].initial = val

    def clean_filters_enabled(self):
        return self.cleaned_data["filters_enabled"] or []


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ("id", "name", "link_name")
    search_fields = ("name", "link_name")


# @admin.register(Gallery)
# class GaleryAdmin(admin.ModelAdmin):
#     list_display = ('name',)


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
    list_display = ("name",)
    search_fields = ("name", "description")


from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "description")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
