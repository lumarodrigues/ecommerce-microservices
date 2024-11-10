from datetime import datetime
from mongoengine import (
    Document, StringField, DecimalField, IntField, FloatField, ReferenceField,
    EmbeddedDocument, EmbeddedDocumentField, ListField, URLField, DateTimeField, ObjectIdField
)
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Category(Document):
    name = StringField(max_length=255, required=True)

    def __str__(self):
        return self.name


class Brand(Document):
    name = StringField(max_length=255, required=True)

    def __str__(self):
        return self.name


class ProductAttribute(EmbeddedDocument):
    key = StringField(required=True)
    value = StringField(required=True)


class Product(Document):
    name = StringField(max_length=255, required=True)
    description = StringField()
    stock = IntField(min_value=0, default=0)
    price = DecimalField(min_value=0, precision=2, required=True)
    image = URLField(required=True)
    brand = ReferenceField(Brand, required=False)
    category = ReferenceField(Category, required=False)
    attributes = ListField(EmbeddedDocumentField(ProductAttribute))
    sku = StringField(max_length=100, unique=True)  # SKU
    discount_percentage = FloatField(min_value=0.0, max_value=100.0, default=0.0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    @property
    def available(self):
        return self.stock > 0

    @property
    def discounted_price(self):
        """Calculates the final price after the discount."""
        if self.discount_percentage > 0:
            return self.price * (1 - (self.discount_percentage / 100))
        return self.price

    def save(self, *args, **kwargs):
        """Override save method to update 'updated_at' field."""
        self.updated_at = datetime.utcnow()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CustomerReview(Document):
    product = ReferenceField(Product, required=True)
    customer_name = StringField(required=True)
    rating = FloatField(min_value=1.0, max_value=5.0, required=True)
    comment = StringField()
    date = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars."


@receiver(pre_delete, sender=Brand)
def set_brand_to_none(sender, instance, **kwargs):
    """Remove brand from products before deleting it."""
    Product.objects(brand=instance).update(set__brand=None)

@receiver(pre_delete, sender=Category)
def set_category_to_none(sender, instance, **kwargs):
    """Remove category from products before deleting it."""
    Product.objects(category=instance).update(set__category=None)

@receiver(pre_delete, sender=Product)
def remove_customer_reviews_from_product(sender, instance, **kwargs):
    """Remove customer reviews for products that are no longer in the catalog."""
    CustomerReview.objects(product=instance).delete()
