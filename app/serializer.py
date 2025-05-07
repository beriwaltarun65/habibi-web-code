from rest_framework import serializers
from app.models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, SubCategory



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'phone_no', 'is_vendor']



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'product_name','product_price', 'subcategory','color','product_description']




class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id','product','image')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields =('id','booking_date','delivery_date','status','user','price')

class ReviewSerializer(serializers.Serializer):

    review_text = serializers.CharField(max_length=100)
    rating = serializers.IntegerField()
    product_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    created_at = serializers.DateTimeField()

class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        models = AddToCart
        fields = ('id', 'user', 'product', 'price', 'quantity', 'booking_date', 'delivery_date', 'status', 'shipping_address', 'payment_method')

class  SubCategoryByCategoryIdserializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'
        read_only_fields = ('user','name','image')


class  ProductBySubCategoryIdserializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('product_name','product_price','product_description')



