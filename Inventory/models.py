from django.db import models

# Create your models here.
# Models for Inventory app

class Product(models.Model):
    name = models.CharField(max_length=254)
    price = models.FloatField()
    image = models.ImageField(upload_to="products")
    added_on = models.DateTimeField()
    description = models.TextField()
    category = models.ForeignKey(to="ProductCategory", on_delete=models.CASCADE)

class ProductCategory(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()
    added_on = models.DateTimeField()

