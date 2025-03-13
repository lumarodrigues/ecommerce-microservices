from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, Brand, CustomerReview
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer, CustomerReviewSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['patch'])
    def remove_from_stock(self, request, pk=None):
        try:
            product = self.get_object()
            quantity = request.data.get('quantity', 0)
            if quantity <= 0:
                return Response({"error": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

            if quantity > product.stock:
                return Response({"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)

            product.stock -= quantity
            product.save()

            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CustomerReviewViewSet(viewsets.ModelViewSet):
    queryset = CustomerReview.objects.all()
    serializer_class = CustomerReviewSerializer
