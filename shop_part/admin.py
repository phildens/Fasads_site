# shop_part/admin.py
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import path
from import_export import resources, fields
from import_export import widgets
from import_export.formats import base_formats
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
from .models import ProductBadge, ProductCurrency, SiteSettings
from .excel_exports import build_products_workbook


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


# === Схема безопасного обмена товарами через Excel ===
class StrictForeignKeyWidget(widgets.ForeignKeyWidget):
    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() == "":
            return None
        value = str(value).strip()
        try:
            return self.model.objects.get(**{self.field: value})
        except self.model.DoesNotExist as exc:
            raise ValueError(
                f'Значение «{value}» отсутствует в справочнике «{self.model._meta.verbose_name_plural}».'
            ) from exc
        except self.model.MultipleObjectsReturned as exc:
            raise ValueError(
                f'В справочнике найдено несколько значений «{value}». Обратитесь к администратору.'
            ) from exc


class StrictManyToManyWidget(widgets.ManyToManyWidget):
    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() == "":
            return self.model.objects.none()
        values = [item.strip() for item in str(value).split(self.separator) if item.strip()]
        queryset = self.model.objects.filter(**{f"{self.field}__in": values})
        found = set(queryset.values_list(self.field, flat=True))
        missing = [item for item in values if item not in found]
        if missing:
            raise ValueError(
                "Значения отсутствуют в справочнике: " + ", ".join(missing)
            )
        return queryset


class RussianBooleanWidget(widgets.BooleanWidget):
    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() == "":
            return None
        normalized = str(value).strip().lower()
        if normalized in {"да", "1", "true"}:
            return True
        if normalized in {"нет", "0", "false"}:
            return False
        raise ValueError('Допустимы только значения «Да» или «Нет».')

    def render(self, value, obj=None, **kwargs):
        return "Да" if value else "Нет"


class ProductBadgeWidget(widgets.CharWidget):
    labels_to_values = {label.lower(): value for value, label in ProductBadge.choices}
    values_to_labels = dict(ProductBadge.choices)

    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() == "":
            return None
        normalized = str(value).strip().lower()
        if normalized in self.labels_to_values:
            return self.labels_to_values[normalized]
        if normalized in self.values_to_labels:
            return normalized
        raise ValueError('Допустимы значения «Фаворит», «Акция», «Новинка» или пустая ячейка.')

    def render(self, value, obj=None, **kwargs):
        return self.values_to_labels.get(value, "")


class CurrencyWidget(widgets.CharWidget):
    allowed = {value for value, _ in ProductCurrency.choices}

    def clean(self, value, row=None, **kwargs):
        normalized = str(value or "").strip().upper()
        if normalized not in self.allowed:
            raise ValueError("Допустимые валюты: RUB, USD, UAH, KZT.")
        return normalized


class NullableCharWidget(widgets.CharWidget):
    def __init__(self):
        super().__init__(allow_blank=False)


class ProductResource(resources.ModelResource):
    id = fields.Field(column_name="ID", attribute="id", widget=widgets.IntegerWidget())
    name = fields.Field(column_name="Название товара", attribute="name", widget=widgets.CharWidget())
    category = fields.Field(column_name="Категория", attribute="category", widget=StrictForeignKeyWidget(Category, "name"))
    manufacturer = fields.Field(column_name="Производитель", attribute="manufacturer", widget=StrictForeignKeyWidget(Manufactor, "name"))
    type_material = fields.Field(column_name="Вид материала", attribute="type_material", widget=StrictForeignKeyWidget(TypeMaterial, "name"))
    product_type = fields.Field(column_name="Тип товара", attribute="product_type", widget=StrictForeignKeyWidget(ProductType, "name"))
    color = fields.Field(column_name="Цвет", attribute="color", widget=StrictForeignKeyWidget(Color, "name"))
    formats = fields.Field(column_name="Форматы", attribute="formats", widget=StrictManyToManyWidget(Format, field="name", separator=";"))
    emptiness = fields.Field(column_name="Пустотность", attribute="emptiness", widget=StrictManyToManyWidget(Emptiness, field="name", separator=";"))
    frosen_defend = fields.Field(column_name="Морозостойкость", attribute="frosen_defend", widget=StrictForeignKeyWidget(FrosenDefender, "name"))
    strength_grade = fields.Field(column_name="Марка прочности", attribute="strength_grade", widget=StrictForeignKeyWidget(StrengthGrade, "name"))
    water_resistance = fields.Field(column_name="Водопоглощение", attribute="water_resistance", widget=StrictForeignKeyWidget(WaterResistance, "name"))
    description = fields.Field(column_name="Описание", attribute="description", widget=NullableCharWidget())
    price = fields.Field(column_name="Актуальная цена", attribute="price", widget=widgets.DecimalWidget())
    old_price = fields.Field(column_name="Старая цена", attribute="old_price", widget=widgets.DecimalWidget())
    currency = fields.Field(column_name="Валюта", attribute="currency", widget=CurrencyWidget())
    promo_tag = fields.Field(column_name="Метка товара", attribute="promo_tag", widget=ProductBadgeWidget())
    priority = fields.Field(column_name="Приоритет", attribute="priority", widget=widgets.IntegerWidget())
    feed_enabled = fields.Field(column_name="Включать в Яндекс-фид", attribute="feed_enabled", widget=RussianBooleanWidget())
    feed_id2 = fields.Field(column_name="ID2", attribute="feed_id2", widget=widgets.CharWidget())
    custom_label_0 = fields.Field(column_name="custom_label_0", attribute="custom_label_0", widget=widgets.CharWidget())
    custom_label_1 = fields.Field(column_name="custom_label_1", attribute="custom_label_1", widget=widgets.CharWidget())
    custom_label_2 = fields.Field(column_name="custom_label_2", attribute="custom_label_2", widget=widgets.CharWidget())
    custom_label_3 = fields.Field(column_name="custom_label_3", attribute="custom_label_3", widget=widgets.CharWidget())
    custom_label_4 = fields.Field(column_name="custom_label_4", attribute="custom_label_4", widget=widgets.CharWidget())
    custom_score = fields.Field(column_name="custom_score", attribute="custom_score", widget=widgets.IntegerWidget())
    product_price = fields.Field(column_name="Прайс-лист товара", attribute="product_price", widget=NullableCharWidget())

    field_order = (
        "id", "name", "category", "manufacturer", "type_material", "product_type",
        "color", "formats", "emptiness", "frosen_defend", "strength_grade",
        "water_resistance", "description", "price", "old_price", "currency",
        "promo_tag", "priority", "feed_enabled", "feed_id2", "custom_label_0",
        "custom_label_1", "custom_label_2", "custom_label_3", "custom_label_4",
        "custom_score", "product_price",
    )

    class Meta:
        model = Product
        fields = field_order = (
            "id", "name", "category", "manufacturer", "type_material", "product_type",
            "color", "formats", "emptiness", "frosen_defend", "strength_grade",
            "water_resistance", "description", "price", "old_price", "currency",
            "promo_tag", "priority", "feed_enabled", "feed_id2", "custom_label_0",
            "custom_label_1", "custom_label_2", "custom_label_3", "custom_label_4",
            "custom_score", "product_price",
        )
        import_id_fields = ("id",)
        import_order = field_order
        export_order = field_order
        clean_model_instances = True
        skip_unchanged = True
        report_skipped = True
        use_bulk = False

    def before_import(self, dataset, **kwargs):
        expected_headers = {field.column_name for field in self.get_import_fields()}
        actual_headers = set(dataset.headers or [])
        missing_headers = sorted(expected_headers - actual_headers)
        if missing_headers:
            raise ValidationError(
                "В файле отсутствуют обязательные столбцы: " + ", ".join(missing_headers)
            )

        seen_ids = set()
        duplicate_ids = set()
        for row in dataset.dict:
            raw_id = row.get("ID")
            if raw_id in (None, ""):
                continue
            try:
                product_id = int(raw_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError(f"Некорректный ID: {raw_id}") from exc
            if product_id in seen_ids:
                duplicate_ids.add(product_id)
            seen_ids.add(product_id)
        if duplicate_ids:
            raise ValidationError(
                "В файле повторяются ID: " + ", ".join(map(str, sorted(duplicate_ids)))
            )

    def before_import_row(self, row, **kwargs):
        raw_id = row.get("ID")
        if raw_id not in (None, ""):
            try:
                product_id = int(raw_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError({"ID": f"Некорректный ID: {raw_id}"}) from exc
            try:
                existing_product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise ValidationError({
                    "ID": f"Товар с ID {product_id} не найден. Для нового товара оставьте ID пустым."
                })
            for column_name, attribute in (
                ("Описание", "description"),
                ("Прайс-лист товара", "product_price"),
            ):
                if row.get(column_name) in (None, "") and getattr(existing_product, attribute) in (None, ""):
                    row[column_name] = getattr(existing_product, attribute)


# === 2. Обновляем ProductAdmin ===
# Меняем admin.ModelAdmin на ImportExportModelAdmin
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    change_list_template = "admin/shop_part/product/change_list.html"
    inlines = [GalleryInline, ]
    list_display = ('name', 'price', 'old_price', 'currency', 'feed_enabled', 'priority', 'promo_tag')
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
        ('Цена и Яндекс-фид', {
            'fields': (
                ('price', 'old_price', 'currency'),
                'feed_enabled', 'feed_id2',
                'custom_label_0', 'custom_label_1', 'custom_label_2',
                'custom_label_3', 'custom_label_4', 'custom_score',
            )
        }),
    )


    def get_import_formats(self):
        return [base_formats.XLSX]

    def get_import_data_kwargs(self, **kwargs):
        import_kwargs = super().get_import_data_kwargs(**kwargs)
        import_kwargs.update(
            use_transactions=True,
            rollback_on_validation_errors=True,
        )
        return import_kwargs

    def get_urls(self):
        custom_urls = [
            path(
                "download-update-excel/",
                self.admin_site.admin_view(self.download_update_excel),
                name="shop_part_product_download_update_excel",
            ),
        ]
        return custom_urls + super().get_urls()

    def download_update_excel(self, request):
        if not self.has_view_or_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        queryset = (
            Product.objects.all()
            .select_related(
                "category", "manufacturer", "type_material", "product_type", "color",
                "frosen_defend", "strength_grade", "water_resistance",
            )
            .prefetch_related("formats", "emptiness")
            .order_by("id")
        )
        dataset = ProductResource().export(queryset)
        reference_lists = {
            "Категория": Category.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Производитель": Manufactor.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Вид материала": TypeMaterial.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Тип товара": ProductType.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Цвет": Color.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Форматы": Format.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Пустотность": Emptiness.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Морозостойкость": FrosenDefender.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Марка прочности": StrengthGrade.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Водопоглощение": WaterResistance.objects.order_by("name").values_list("name", flat=True).distinct(),
            "Валюта": [value for value, _ in ProductCurrency.choices],
            "Метка товара": [label for _, label in ProductBadge.choices],
            "Включать в Яндекс-фид": ["Да", "Нет"],
        }
        output = build_products_workbook(dataset, reference_lists)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="products-update.xlsx"'
        return response


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
    list_display = ('title', 'background_theme', 'image_only')
    list_filter = ('background_theme', 'image_only')
    search_fields = ('title', 'subtitle', 'description')
    fieldsets = (
        ('Вид баннера', {
            'fields': ('background_theme', 'image_only'),
        }),
        ('Текст и кнопка', {
            'fields': ('title', 'subtitle', 'description', 'cta_url'),
            'description': 'Для режима "Только картинка" поля можно оставить пустыми.',
        }),
        ('Изображения', {
            'fields': ('image', 'image_mobile'),
        }),
    )
