

from django.db import models
from django.contrib.auth.models import User

# Create your models here
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    image = models.ImageField(upload_to="subcategory_images/", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=80)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    stock = models.IntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product_name

        

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    
    def __str__(self):
        return f"Image for {self.product.product_name}"



class AddToCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.product.product_name} in {self.user.username}'s cart"


class Order(models.Model):
    STATUS = [
        ('delivered', 'delivered'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
        ('pending', 'pending'),
    ]

    PAYMENT_METHODS = [
        ('credit_card', 'credit_card'),
        ('phone_pay', 'phone_pay'),
        ('paytm', 'paytm'),
        ('bank_transfer', 'bank_transfer')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)  


    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)]) 
    review_text = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    is_vendor = models.BooleanField(default=True)
    phone_no = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}"