from django.db import models
from django.conf import settings


class CategoryType(models.TextChoices):
    INCOME = 'INCOME', 'Income'
    EXPENSE = 'EXPENSE', 'Expense'


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#000000')
    type = models.CharField(max_length=10, choices=CategoryType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Null for default categories, set for custom user categories"
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'user']
        
    def __str__(self):
        return f"{self.name} ({self.type})"


class AccountType(models.TextChoices):
    CHECKING = 'CHECKING', 'Checking'
    SAVINGS = 'SAVINGS', 'Savings'
    INVESTMENT = 'INVESTMENT', 'Investment'
    CREDIT = 'CREDIT', 'Credit Card'
    CASH = 'CASH', 'Cash'


class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    type = models.CharField(max_length=15, choices=AccountType.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'user']
        
    def __str__(self):
        return f"{self.name} ({self.user.email})"
