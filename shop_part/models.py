from django.db import models
from django.core.exceptions import ValidationError
import re


class SiteSettings(models.Model):
    """Глобальные настройки сайта (singleton)."""
    email = models.EmailField("Электронная почта для контактов", blank=True, null=True)
    phone = models.CharField("Телефон для контактов", max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    @property
    def phone_href(self) -> str | None:
        if not self.phone:
            return None
        # оставим + и цифры
        cleaned = re.sub(r"[^\d+]", "", self.phone)
        return f"tel:{cleaned}"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1  # держим одну запись
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TypeMaterial(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Вид материала"
        verbose_name_plural = "Виды материалов"

    def __str__(self):
        return self.name


class FilterKey(models.TextChoices):
    MANUFACTURER = "manufacturer", "Производитель"
    COLOR = "color", "Цвет"
    TYPE_MATERIAL = "type_material", "Вид материала"
    PRODUCT_TYPE = "product_type", "Тип товара"
    FROSEN_DEFEND = "frosen_defend", "Морозостойкость"
    STRENGTH_GRADE = "strength_grade", "Марка прочности"
    WATER_RESISTANCE = "water_resistance", "Водопоглощение"
    FORMAT = "format", "Формат"  # M2M formats
    EMPTINESS = "emptiness", "Пустотность"  # M2M emptiness


class Category(models.Model):
    name = models.CharField(max_length=100)
    link_name = models.CharField(max_length=100, null=True)
    card_image = models.ImageField(null=True, blank=True)
    filters_enabled = models.JSONField(default=list, blank=True,
                                       help_text="Список ключей фильтров из FilterKey.*")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def clean(self):
        # валидация, чтобы ключи были только из перечисления
        if self.filters_enabled:
            allowed = {c.value for c in FilterKey}
            bad = [x for x in self.filters_enabled if x not in allowed]
            if bad:
                raise ValidationError({"filters_enabled": f"Неизвестные ключи: {bad}"})
        return super().clean()

    def __str__(self):
        return self.name


class Format(models.Model):
    name = models.CharField(max_length=100, verbose_name="Формат")

    class Meta:
        verbose_name = "Формат"
        verbose_name_plural = "Форматы"

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100, verbose_name="Цвет")

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name


class FrosenDefender(models.Model):
    name = models.CharField(max_length=100, verbose_name="Марка прочности")

    class Meta:
        verbose_name = "Марка прочности"
        verbose_name_plural = "Марка прочности"

    def __str__(self):
        return self.name


class Manufactor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Производитель")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name


class StrengthGrade(models.Model):
    name = models.CharField(max_length=100, verbose_name="Морозостойкость")

    class Meta:
        verbose_name = "Морозостойкость"
        verbose_name_plural = "Морозостойкость"

    def __str__(self):
        return self.name


class WaterResistance(models.Model):
    name = models.CharField(max_length=100, verbose_name="Водопоглощение")

    class Meta:
        verbose_name = "Водопоглощение"
        verbose_name_plural = "Водопоглощение"

    def __str__(self):
        return self.name


class Emptiness(models.Model):
    name = models.CharField(max_length=100, verbose_name="Пустотность")

    class Meta:
        verbose_name = "Пустотность"
        verbose_name_plural = "Пустотность"

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип товара")

    class Meta:
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"

    def __str__(self):
        return self.name


class ProductBadge(models.TextChoices):
    FAVORITE = "favorite", "Фаворит"
    SALE = "sale", "Акция"
    NEW = "new", "Новинка"


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название товара")
    card_image = models.ImageField(null=True, blank=True, verbose_name="Фото карточки")
    manufacturer = models.ForeignKey(Manufactor, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name="Производитель")
    type_material = models.ForeignKey(TypeMaterial, on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name="Вид материала")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    formats = models.ManyToManyField(Format, blank=True, verbose_name="Форматы")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Цвет")
    frosen_defend = models.ForeignKey(FrosenDefender, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Марка прочности")
    strength_grade = models.ForeignKey(StrengthGrade, on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name="Морозостойкость")
    water_resistance = models.ForeignKey(WaterResistance, on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Водопоглощение")
    emptiness = models.ManyToManyField(Emptiness, blank=True, verbose_name="Пустотность")
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name="Тип товара")
    product_price = models.TextField(blank=True, null=True, verbose_name="Прайс лист товара")
    promo_tag = models.CharField(
        "Метка товара",
        max_length=16,
        choices=ProductBadge.choices,
        blank=True,
        null=True,
        help_text="Отображается как бейдж на карточке: Фаворит / Акция / Новинка"
    )
    # НОВОЕ: ручной выбор похожих товаров
    similar_products_manual = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='manually_recommended_for',
        verbose_name="Похожие товары (ручной выбор)"
    )

    priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Приоритет сортировки (чем больше — выше)"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("-priority", "-id")

    def __str__(self):
        name = self.name
        if self.manufacturer:
            name = name + " " + self.manufacturer.name

        if self.product_type:
            name = name + " " + self.product_type.name
        return name


class Gallery(models.Model):
    image = models.ImageField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')


class Questions(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


# Форма обратной связи
class ContactRequest(models.Model):
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=30, blank=True)
    description = models.TextField("Краткое описание", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на обратный звонок"
        verbose_name_plural = "Заявки на обратный звонок"

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.email}"


class BigGalery(models.Model):
    position = models.IntegerField(default=0, help_text='Позиция в списке', verbose_name='позиция в списке')
    name = models.CharField(max_length=100, help_text="Имя объекта", verbose_name="имя(текст на картинке)")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Товар отображаемый при наведении на точку")
    card_image = models.ImageField(null=True, blank=True, help_text="Изображение в галерее",
                                   verbose_name='Фото карточки объекта в общем списке')
    our_supplies = models.BooleanField(null=True, blank=True, verbose_name='Наши поставки')

    class Meta:
        verbose_name = "Галерея объектов"
        verbose_name_plural = "Галерея объектов"

    def __str__(self):
        return self.name


class SmallGallery(models.Model):
    image = models.ImageField(verbose_name='Фото объекта')
    object = models.ForeignKey(BigGalery, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Фото объекта при открытии'
        verbose_name_plural = ('Фото объекта при открытии')

class BannerSlide(models.Model):
    title = models.CharField('Заголовок (большой)', max_length=200)
    subtitle = models.CharField('Подзаголовок (средний)', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Картинка', upload_to='banners/')
    cta_url = models.URLField('Ссылка для кнопки «Узнать подробнее»')
    image_mobile = models.ImageField('Картинка (мобильная версия)', upload_to='banners/', blank=True, null=True)

    def __str__(self):
        return self.title