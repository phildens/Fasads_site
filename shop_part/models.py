from django.db import models


class TypeMaterial(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    link_name = models.CharField(max_length=100, null=True)
    card_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name


class Format(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FrosenDefender(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Марка прочности"
        verbose_name_plural = "Марка прочности"
    def __str__(self):
        return self.name


class Manufactor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StrengthGrade(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Морозостойкость"
        verbose_name_plural = "Морозостойкость"
    def __str__(self):
        return self.name


class WaterResistance(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Emptiness(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    card_image = models.ImageField(null=True, blank=True)
    manufacturer = models.ForeignKey(Manufactor, on_delete=models.SET_NULL, null=True, blank=True)
    type_material = models.ForeignKey(TypeMaterial, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    formats = models.ManyToManyField(Format)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    frosen_defend = models.ForeignKey(FrosenDefender, on_delete=models.SET_NULL, null=True)
    strength_grade = models.ForeignKey(StrengthGrade, on_delete=models.SET_NULL, null=True)
    water_resistance = models.ForeignKey(WaterResistance, on_delete=models.SET_NULL, null=True)
    emptiness = models.ManyToManyField(Emptiness)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + " " + self.manufacturer.name + " " + self.product_type.name


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
    first_name   = models.CharField("Имя", max_length=100)
    last_name    = models.CharField("Фамилия", max_length=100, blank=True)
    email        = models.EmailField("Email")
    phone        = models.CharField("Телефон", max_length=30, blank=True)
    description  = models.TextField("Краткое описание", blank=True)
    created_at   = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на обратный звонок"
        verbose_name_plural = "Заявки на обратный звонок"

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.email}"


class BigGalery(models.Model):
    position = models.IntegerField(default=0, help_text='Позиция в списке', verbose_name='позиция в списке')
    name = models.CharField(max_length=100, help_text="Имя объекта", verbose_name="имя(текст на картинке)")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Товар отображаемый при наведении на точку")
    card_image = models.ImageField(null=True, blank=True, help_text="Изображение в галерее", verbose_name='Фото карточки объекта в общем списке')

    class Meta:
        verbose_name = "Галерея объектов"
        verbose_name_plural = "Галерея объектов"

    def __str__(self):
        return self.name

class SmallGallery(models.Model):
    image = models.ImageField(verbose_name='Фото объекта')
    object = models.ForeignKey(BigGalery, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name='Фото объекта при открытии'
        verbose_name_plural=('Фото объекта при открытии')

