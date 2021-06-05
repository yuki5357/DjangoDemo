from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField("Name", max_length=100, default="")
    email = models.EmailField("Email")

class Book(models.Model):
    title = models.CharField("Title", max_length=100, default="")
    authors = models.ManyToManyField(Author, default="")
    year = models.CharField("Year", max_length=64, default="")
