from rest_framework import serializers
from .models import Category, Account, Asset


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color', 'type', 'is_default', 'created_at']
        read_only_fields = ['id', 'is_default', 'created_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AssetSerializer(serializers.ModelSerializer):
    gain_loss = serializers.ReadOnlyField()
    gain_loss_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'current_value', 'purchase_price', 
            'purchase_date', 'description', 'is_active', 'gain_loss', 
            'gain_loss_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'gain_loss', 'gain_loss_percentage', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)