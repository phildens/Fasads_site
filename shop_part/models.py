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

    def __str__(self):
        return self.name


class Manufactor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StrengthGrade(models.Model):
    name = models.CharField(max_length=100)

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
    strength_grade = models.ManyToManyField(StrengthGrade)
    water_resistance = models.ForeignKey(WaterResistance, on_delete=models.SET_NULL, null=True)
    emptiness = models.ManyToManyField(Emptiness)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)




    def __str__(self):
        return self.name + " " + self.type.name


class Questions(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
