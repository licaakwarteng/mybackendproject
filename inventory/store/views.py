from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.generics import ListAPIView, CreateAPIView
from .models import Product, Category, InventoryChange
from .serializers import ProductSerializer, InventoryChangeSerializer
from .models import Product
from .serializers import ProductSerializer

def index(request):
    return HttpResponse("Welcome to our store!")

class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return "Get the products created"

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.ModelSerializer  # Placeholder; you can create a CategorySerializer if you want.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category__name', 'description']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    ordering = ['name']

    def get_queryset(self):
        """
        Only return products owned by the logged-in user.
        """
        user = self.request.user
        queryset = Product.objects.filter(owner=user)

        # Optional filters
        category = self.request.query_params.get('category')
        low_stock = self.request.query_params.get('low_stock')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')

        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if low_stock:
            queryset = queryset.filter(quantity__lt=int(low_stock))
        if price_min and price_max:
            queryset = queryset.filter(price__gte=price_min, price__lte=price_max)

        return queryset

    def perform_create(self, serializer):
        """
        Automatically set the product owner to the logged-in user.
        """
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def adjust_stock(self, request, pk=None):
        """
        Custom endpoint to adjust stock and log changes.
        Example body:
        {
            "new_quantity": 25,
            "reason": "Restocked from supplier"
        }
        """
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        new_quantity = request.data.get('new_quantity')
        reason = request.data.get('reason', '')

        if new_quantity is None:
            return Response({"error": "new_quantity is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_quantity = int(new_quantity)
        except ValueError:
            return Response({"error": "new_quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        old_quantity = product.quantity
        delta = new_quantity - old_quantity

        # Update product
        product.quantity = new_quantity
        product.save()

        # Log the change
        InventoryChange.objects.create(
            product=product,
            changed_by=request.user,
            previous_quantity=old_quantity,
            new_quantity=new_quantity,
            delta=delta,
            reason=reason
        )

        return Response({"message": f"Stock updated successfully. Change: {delta}"}, status=status.HTTP_200_OK)


# -----------------------------
# INVENTORY CHANGE VIEWSET
# -----------------------------
class InventoryChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View all stock change history (read-only)
    """
    serializer_class = InventoryChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return InventoryChange.objects.filter(product__owner=user).select_related('product', 'changed_by')