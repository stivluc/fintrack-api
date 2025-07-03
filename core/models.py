from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


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


class AssetType(models.TextChoices):
    REAL_ESTATE = 'REAL_ESTATE', 'Immobilier'
    STOCKS = 'STOCKS', 'Actions'
    BONDS = 'BONDS', 'Obligations'
    INSURANCE = 'INSURANCE', 'Assurance vie'
    SAVINGS_ACCOUNT = 'SAVINGS_ACCOUNT', 'Livret A'
    PENSION_PLAN = 'PENSION_PLAN', 'PEL'
    CHECKING_ACCOUNT = 'CHECKING_ACCOUNT', 'Compte courant'
    CRYPTO = 'CRYPTO', 'Crypto'
    PRECIOUS_METALS = 'PRECIOUS_METALS', 'Or/Métaux'
    BUSINESS = 'BUSINESS', 'Entreprise'
    OTHER = 'OTHER', 'Autre'


class Asset(models.Model):
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    current_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    purchase_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True, 
        blank=True
    )
    purchase_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'user']
        ordering = ['-current_value']
        
    def __str__(self):
        return f"{self.name} ({self.asset_type}) - €{self.current_value}"
    
    @property
    def gain_loss(self):
        if self.purchase_price:
            return self.current_value - self.purchase_price
        return None
    
    @property
    def gain_loss_percentage(self):
        if self.purchase_price and self.purchase_price > 0:
            return ((self.current_value - self.purchase_price) / self.purchase_price) * 100
        return None
