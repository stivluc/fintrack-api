from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import json


class Transaction(models.Model):
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    category = models.ForeignKey('core.Category', on_delete=models.CASCADE)
    account = models.ForeignKey('core.Account', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_recurring = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"{self.description} - {self.amount}€ ({self.date.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        if self.category.type == 'EXPENSE':
            self.amount = abs(self.amount) * -1
        else:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)


class BudgetPeriod(models.TextChoices):
    MONTHLY = 'MONTHLY', 'Monthly'
    YEARLY = 'YEARLY', 'Yearly'


class Budget(models.Model):
    category = models.ForeignKey('core.Category', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    period = models.CharField(
        max_length=10, 
        choices=BudgetPeriod.choices, 
        default=BudgetPeriod.MONTHLY
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['category', 'user', 'period']
        
    def __str__(self):
        return f"{self.category.name} - {self.monthly_limit}€/{self.period.lower()}"
    
    @property
    def yearly_limit(self):
        if self.period == BudgetPeriod.YEARLY:
            return self.monthly_limit
        return self.monthly_limit * 12
