# shop_part/proxies.py
from .models import (
    TypeMaterial, Category, Format, Color, FrosenDefender, Manufactor,
    StrengthGrade, WaterResistance, Emptiness, ProductType,
    Gallery, BigGalery, SmallGallery
)

# === ХАРАКТЕРИСТИКИ ===
class CategoryChar(Category):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class TypeMaterialChar(TypeMaterial):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Вид материала"
        verbose_name_plural = "Виды материалов"

class FormatChar(Format):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Формат"
        verbose_name_plural = "Форматы"

class ColorChar(Color):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

class FrosenDefenderChar(FrosenDefender):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Морозостойкость"
        verbose_name_plural = "Морозостойкость"

class StrengthGradeChar(StrengthGrade):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Марка прочности"
        verbose_name_plural = "Марка прочности"

class WaterResistanceChar(WaterResistance):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Водопоглощение"
        verbose_name_plural = "Водопоглощение"

class ManufactorChar(Manufactor):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

class EmptinessChar(Emptiness):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Пустотность"
        verbose_name_plural = "Пустотность"

class ProductTypeChar(ProductType):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"

# === ГАЛЕРЕЯ ===
class GalleryProxy(Gallery):
    class Meta:
        proxy = True
        app_label = 'characteristics'
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товара"

class BigGaleryProxy(BigGalery):
    class Meta:
        proxy = True
        app_label = 'gallery'
        verbose_name = "Галерея объектов"
        verbose_name_plural = "Галерея объектов"

class SmallGalleryProxy(SmallGallery):
    class Meta:
        proxy = True
        app_label = 'gallery'
        verbose_name = "Фото объекта при открытии"
        verbose_name_plural = "Фото объекта при открытии"
