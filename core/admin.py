from django.contrib import admin
from .models import Category, Account


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'color', 'is_default', 'user', 'created_at']
    list_filter = ['type', 'is_default', 'created_at']
    search_fields = ['name']
    ordering = ['type', 'name']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'balance', 'user', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'user__email']
    ordering = ['user', 'name']
