# shop_part/admin.py
from django.contrib import admin
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Product, FilterKey, Category  # Product остаётся в «Интернет-магазин»
from .proxies import (
    # характеристики
    CategoryChar, TypeMaterialChar, FormatChar, ColorChar, FrosenDefenderChar,
    ManufactorChar, StrengthGradeChar, WaterResistanceChar, EmptinessChar, ProductTypeChar,
    # галерея
    GalleryProxy, BigGaleryProxy, SmallGalleryProxy
)
from .models import (
    Product, Manufactor, TypeMaterial, Category, Color,
    FrosenDefender, StrengthGrade, WaterResistance, ProductType,
    Format, Emptiness, FilterKey
)
from .models import Questions, ContactRequest  # куда хотите, можно оставить в «Интернет-магазин»
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fields = ("email", 'phone')

    def has_add_permission(self, request):
        # запретим создавать больше одной записи
        return not SiteSettings.objects.exists()


# ====== ТОВАРЫ (Интернет-магазин) ======
class GalleryInline(admin.TabularInline):
    model = GalleryProxy  # используем прокси, работает как и раньше
    fk_name = 'product'
    extra = 0


# === 1. Создаем "Ресурс" (Схему выгрузки) ===
class ProductResource(resources.ModelResource):
    # Настраиваем поля ForeignKey (чтобы выводилось имя, а не ID)
    manufacturer = fields.Field(
        column_name='Производитель',
        attribute='manufacturer',
        widget=ForeignKeyWidget(Manufactor, 'name')
    )
    type_material = fields.Field(
        column_name='Вид материала',
        attribute='type_material',
        widget=ForeignKeyWidget(TypeMaterial, 'name')
    )
    category = fields.Field(
        column_name='Категория',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    color = fields.Field(
        column_name='Цвет',
        attribute='color',
        widget=ForeignKeyWidget(Color, 'name')
    )
    frosen_defend = fields.Field(
        column_name='Морозостойкость',
        attribute='frosen_defend',
        widget=ForeignKeyWidget(FrosenDefender, 'name')
    )
    strength_grade = fields.Field(
        column_name='Марка прочности',
        attribute='strength_grade',
        widget=ForeignKeyWidget(StrengthGrade, 'name')
    )
    water_resistance = fields.Field(
        column_name='Водопоглощение',
        attribute='water_resistance',
        widget=ForeignKeyWidget(WaterResistance, 'name')
    )
    product_type = fields.Field(
        column_name='Тип товара',
        attribute='product_type',
        widget=ForeignKeyWidget(ProductType, 'name')
    )

    # Настраиваем поля ManyToMany (список через запятую)
    formats = fields.Field(
        column_name='Форматы',
        attribute='formats',
        widget=ManyToManyWidget(Format, field='name', separator=', ')
    )
    emptiness = fields.Field(
        column_name='Пустотность',
        attribute='emptiness',
        widget=ManyToManyWidget(Emptiness, field='name', separator=', ')
    )

    # Сюда добавим метод для красивого вывода choices (Promo tag)
    promo_tag_display = fields.Field(column_name='Метка (Promo)')

    class Meta:
        model = Product
        # Список полей, которые будут в Excel (в нужном порядке)
        fields = (
            'id', 'name', 'manufacturer', 'type_material', 'category',
            'product_price', 'promo_tag_display', 'color',
            'formats', 'emptiness', 'description', 'priority'
        )
        export_order = fields

    # Метод для получения человекочитаемого названия метки (Новинка/Акция)
    def dehydrate_promo_tag_display(self, product):
        return product.get_promo_tag_display() if product.promo_tag else ""


# === 2. Обновляем ProductAdmin ===
# Меняем admin.ModelAdmin на ImportExportModelAdmin
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    inlines = [GalleryInline, ]
    list_display = ('name', 'priority', 'card_image', 'type_material', 'description', 'promo_tag')
    list_editable = ('priority',)
    search_fields = (
        "name",
        "description",
        "manufacturer__name",
        "type_material__name",
        "product_type__name",
        "color__name",
        "strength_grade__name",
        "water_resistance__name",
        "frosen_defend__name",
        "formats__name",
        "emptiness__name",
        "category__name",
    )
    list_filter = (
        "type_material",
        "manufacturer",
        "product_type",
        "color",
        "strength_grade",
        "water_resistance",
        "frosen_defend",
        "formats",
        "emptiness",
        "category",
    )

    # НОВОЕ: удобный виджет для выбора похожих
    filter_horizontal = ('similar_products_manual',)

    # НОВОЕ: выведем поле в форму редактирования
    fieldsets = (
        (None, {
            'fields': (
                'name', 'card_image', 'description',
                'manufacturer', 'type_material', 'category',
                'color', 'frosen_defend', 'strength_grade',
                'water_resistance', 'product_type',
                'formats', 'emptiness',
                'product_price', 'promo_tag',
                'similar_products_manual',  # ← добавили сюда
            )
        }),
    )


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


from .models import BannerSlide


@admin.register(BannerSlide)
class BannerSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle')
    search_fields = ('title', 'subtitle', 'description')
