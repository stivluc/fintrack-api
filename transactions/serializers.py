from rest_framework import serializers
from .models import Transaction, Budget
from core.serializers import CategorySerializer, AccountSerializer


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    account_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'date', 'description', 'category', 'account',
            'category_id', 'account_id', 'is_recurring', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
        
    def validate_category_id(self, value):
        user = self.context['request'].user
        try:
            from core.models import Category
            category = Category.objects.get(id=value)
            if category.user and category.user != user:
                raise serializers.ValidationError("Category not found.")
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category not found.")
            
    def validate_account_id(self, value):
        user = self.context['request'].user
        try:
            from core.models import Account
            account = Account.objects.get(id=value, user=user)
            return value
        except Account.DoesNotExist:
            raise serializers.ValidationError("Account not found.")


class BudgetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    yearly_limit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_id', 'monthly_limit', 'yearly_limit',
            'period', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
        
    def validate_category_id(self, value):
        user = self.context['request'].user
        try:
            from core.models import Category
            category = Category.objects.get(id=value)
            if category.user and category.user != user:
                raise serializers.ValidationError("Category not found.")
            if category.type != 'EXPENSE':
                raise serializers.ValidationError("Budgets can only be created for expense categories.")
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category not found.")