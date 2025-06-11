from rest_framework import serializers
from app.models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, SubCategory
from .models import Product, ProductImage



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'is_vendor', 'phone_no']        
   
class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="profile.phone_no", required=False)
    is_vendor = serializers.BooleanField(source="profile.is_vendor", required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'phonen_umber', 'is_vendor']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('username','first_name','last_name','password','email','profile')
        read_only_fields = ('id', 'username', 'email') 



class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')
        read_only = ('user',)




class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name','user']







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







class ProductImageSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(read_only=True)
    class Meta:
        model = ProductImage
        # fields = ('id', 'product', 'image')
        fields = "__all__"

class ProductBysubcategory(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True,read_only=True)
    class Meta:
        model=Product
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__' 

class AddToCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product = ProductSerializer(read_only=True)
    class Meta:
        model = AddToCart
        fields = ['id','user', 'product', 'quantity', 'added_at']



