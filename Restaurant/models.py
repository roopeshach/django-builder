from django.db import models

# Create your models here.
# Models for Restaurant app

class Waiter(models.Model):
    name = models.CharField(max_length=254)
    email = models.CharField(max_length=250)
    address = models.CharField(max_length=254)

class Cook(models.Model):
    name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)

