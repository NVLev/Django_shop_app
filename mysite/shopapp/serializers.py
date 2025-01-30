from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Order, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        user = serializers.CharField(source="user.username")
        # products = serializers.StringRelatedField(many=True)
        products = ProductSerializer(many=True, read_only=True)
        model = Order
        fields = [
            "pk",
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
            "receipt",
        ]
