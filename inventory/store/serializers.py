from .models import Product, Category, InventoryChange
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'owner', 'name', 'description', 'price', 'quantity',
                  'category', 'category_name', 'date_added', 'last_updated']
        read_only_fields = ['id', 'owner', 'date_added', 'last_updated']

    def validate(self, data):
        # Example: prevent duplicate product names per user/category
        user = self.context['request'].user
        name = data.get('name')
        category = data.get('category')

        if Product.objects.filter(name__iexact=name, category=category, owner=user).exists():
            raise serializers.ValidationError("You already have a product with this name in that category.")

        if data.get('price', 0) < 0:
            raise serializers.ValidationError("Price must be non-negative.")

        if data.get('quantity', 0) < 0:
            raise serializers.ValidationError("Quantity must be non-negative.")

        return data
    
class InventoryChangeSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    changed_by = serializers.ReadOnlyField(source='changed_by.username')

    class Meta:
        model = InventoryChange
        fields = [
            'id', 'product', 'product_name', 'changed_by',
            'previous_quantity', 'new_quantity', 'delta', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'changed_by', 'previous_quantity', 'new_quantity', 'delta', 'created_at']
