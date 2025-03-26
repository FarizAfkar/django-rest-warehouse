from rest_framework import serializers
from .models import Item, PurchaseHeader, PurchaseDetail, SellHeader, SellDetail

# Serializer for Login Request
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ItemSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    unit = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    stock = serializers.IntegerField(required=False)
    balance = serializers.IntegerField(required=False)

    class Meta:
        model = Item
        fields = ['code', 'name', 'unit', 'description', 'stock', 'balance']


class PurchaseDetailSerializer(serializers.ModelSerializer):
    item_code = serializers.SlugRelatedField(
        queryset=Item.objects.all(), slug_field='code', required=False
    )
    quantity = serializers.IntegerField(required=True)
    unit_price = serializers.IntegerField(required=True)
    header_code = serializers.SlugRelatedField(
        queryset=PurchaseHeader.objects.all(), slug_field='code', required=False
    )

    class Meta:
        model = PurchaseDetail
        fields = ['item_code', 'quantity', 'unit_price', 'header_code']


class PurchaseHeaderSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    description = serializers.CharField(required=True)
    details = PurchaseDetailSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseHeader
        fields = ['code', 'date', 'description', 'details']


class SellDetailSerializer(serializers.ModelSerializer):
    item_code = serializers.SlugRelatedField(
        queryset=Item.objects.all(), slug_field='code', required=False
    )
    quantity = serializers.IntegerField(required=True)
    header_code = serializers.SlugRelatedField(
        queryset=SellHeader.objects.all(), slug_field='code', required=False
    )

    class Meta:
        model = SellDetail
        fields = ['item_code', 'quantity', 'header_code']


class SellHeaderSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    description = serializers.CharField(required=True)
    details = SellDetailSerializer(many=True, read_only=True)

    class Meta:
        model = SellHeader
        fields = ['code', 'date', 'description', 'details']