from django.contrib import admin
from .models import Transaction, Budget


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'category', 'account', 'user', 'is_recurring']
    list_filter = ['category__type', 'is_recurring', 'date', 'created_at']
    search_fields = ['description', 'user__email', 'category__name']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'monthly_limit', 'period', 'user', 'is_active', 'created_at']
    list_filter = ['period', 'is_active', 'created_at']
    search_fields = ['category__name', 'user__email']
    ordering = ['user', 'category__name']
