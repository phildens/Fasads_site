from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
 

class WaterResistant(models.Model):
    name = models.CharField(max_length=100)


class Strength(models.Model):
    name = models.CharField(max_length=100)

class Format(models.Model):
    name = models.CharField(max_length=100)

class Type(models.Model):
    name = models.CharField(max_length=100)

class Kind(models.Model):
    name = models.CharField(max_length=100)

class Color(models.Model):
    name = models.CharField(max_length=100)


class Manifacter(models.Model):
    name = models.CharField(max_length=100)


class FreezeDefend(models.Model):
    name = models.CharField(max_length=100)


