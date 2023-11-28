from django.db import models

# Create your models here.
# Models for Website app

class Blog(models.Model):
    title = models.CharField(max_length=254)
    content = models.TextField()
    date = models.DateTimeField()
    author = models.CharField(max_length=254)
    image = models.ImageField(upload_to="blogs")

class Service(models.Model):
    title = models.CharField(max_length=254)
    description = models.TextField()
    image = models.ImageField(upload_to="services")
    icon = models.CharField(max_length=254)

