from django.db import models


class Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    link_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    card_image = models.ImageField(null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.type.name
