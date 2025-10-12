from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    description = models.TextField(default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class InventoryChange(models.Model):
    """
    Track any stock changes (restock, sale, correction, etc.)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='changes')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    delta = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} change ({self.delta}) by {self.changed_by}"


   

