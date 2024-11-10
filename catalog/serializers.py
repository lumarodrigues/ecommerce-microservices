from rest_framework import serializers
from .models import Category, Brand, Product, CustomerReview, ProductAttribute


class ProductAttributeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    key = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)
        return representation

    def create(self, validated_data):
        category = Category(**validated_data)
        category.save()
        return category

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class BrandSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)
        return representation

    def create(self, validated_data):
        brand = Brand(**validated_data)
        brand.save()
        return brand

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(allow_blank=True)
    stock = serializers.IntegerField(default=0)
    price = serializers.FloatField(required=True)
    image = serializers.URLField(required=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    attributes = ProductAttributeSerializer(many=True, required=False)
    sku = serializers.CharField(max_length=100, required=True, allow_blank=False)
    discount_percentage = serializers.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)

        if instance.brand:
            representation['brand'] = {
                'id': str(instance.brand.id),
                'name': instance.brand.name
            }

        if instance.category:
            representation['category'] = {
                'id': str(instance.category.id),
                'name': instance.category.name
            }

        return representation

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        product = Product(**validated_data)
        product.save()

        for attribute_data in attributes_data:
            attribute = ProductAttribute(**attribute_data)
            product.attributes.append(attribute)
        product.save()
        return product

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.price = validated_data.get('price', instance.price)
        instance.image = validated_data.get('image', instance.image)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.category = validated_data.get('category', instance.category)
        instance.sku = validated_data.get('sku', instance.sku)
        instance.discount_percentage = validated_data.get('discount_percentage', instance.discount_percentage)

        if attributes_data is not None:
            instance.attributes = []
            for attribute_data in attributes_data:
                attribute = ProductAttribute(**attribute_data)
                instance.attributes.append(attribute)

        instance.save()
        return instance


class CustomerReviewSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    product_id = serializers.CharField(max_length=100)
    rating = serializers.IntegerField()
    review = serializers.CharField(allow_blank=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)
        representation['product_id'] = str(instance.product.id)
        return representation

    def create(self, validated_data):
        review = CustomerReview(**validated_data)
        review.save()
        return review

    def update(self, instance, validated_data):
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.review = validated_data.get('review', instance.review)
        instance.save()
        return instance
