
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect,HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Category, SubCategory, Product, Profile,  ProductImage, Order, AddToCart, Review
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import date
from django.db.models import Avg
from rest_framework.viewsets import ModelViewSet
from .serializer import *
from .serializer import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import Product
from .serializer import ProductSerializer,UserSerializer,ProfileSerializer
from rest_framework import generics,filters
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# import django_filters
# from django_filters.filters import *
from rest_framework.views import APIView



class ProductBySubcategoryViewset(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductBysubcategory

    def retrieve(self, request, *args, **kwargs):
        _id = kwargs['pk']
        product=Product.objects.filter(subcategory = _id)
        serializers = ProductBysubcategory(product, many=True, context={'request': request})
        # serializers=ProductBysubcategory(product,many=True,)
        return Response(serializers.data,status=status.HTTP_200_OK)
    

class ProductSearchAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('search')
      
        if query:
            return queryset.filter(
                Q(product_name__icontains=query) |
                Q(product_description__icontains=query)|
                Q(color__icontains=query)

            )
        return queryset

# class ProductSearchAPIView(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         query = self.request.query_params.get('search')
#         if query:
#             return queryset.filter(
#                 Q(product_name__icontains=query) |
#                 Q(product_description__icontains=query) |
#                 Q(color__icontains=query)
#             )
#         return queryset





class SubCategoryByCategoryIdViewSet(ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoryByCategoryIdserializer

    def retrieve(self, request, *args, **kwargs):
        category_id = kwargs['pk']
        subcategory = SubCategory.objects.filter(category_id = category_id)

        return Response(SubCategoryByCategoryIdserializer(subcategory,many=True).data,status=status.HTTP_200_OK) 
    
class SubCategoryByCategoryViewset(ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoryByCategoryIdserializer        

    def retrieve(self, request, *args, **kwargs):
        _id = kwargs['pk']
        sub = SubCategory.objects.filter(category = _id)
        serializer=SubCategoryByCategoryIdserializer(sub,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    
   


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer  
    permission_classes = (permissions.AllowAny,)
    

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data['username']
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        password = data['password']
        phone_no = data['profile']['phone_no']
        is_vendor = data['profile'].get('is_vendor', False)
        
        if User.objects.filter(username=username).exists():
           return Response({'error':'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password
        )   

        Profile.objects.create(
            user = user,
            phone_no = phone_no,
            is_vendor = is_vendor
        )

        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    try:
        profile = user.profile  
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_no": profile.phone_no,
            "is_vendor": profile.is_vendor
        })
    except Profile.DoesNotExist:
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_no" :"",
            "is_vendor": False 
        })


class CategoryViewset(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
   
    
    # permission_classes = [IsVendor]

    def create(self, request, *args, **kwargs):
        # breakpoint()
        image = request.FILES.get('image')
        name = request.data.get('name')
        user_id = request.user.id
        category = Category.objects.create(
            name = name,
            image = image,
            user_id = user_id
        )

        category.save()
        category_serialzier = CategorySerializer(category)

        return Response(category_serialzier.data, status=status.HTTP_201_CREATED)
    

class SubCategoryViewset(ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def create(self, request, *args, **kwargs):
        category_id = request.data.get('category')
        category = Category.objects.get(id=category_id)
        subcategory = SubCategory.objects.create(
            name=request.data.get('name'),
            category=category,
            user=request.user
        )
        serializer = self.get_serializer(subcategory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ProductImageViewset(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer




class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        images = request.FILES.getlist('images')

        subcategory_id = data.get('subcategory')

        if not subcategory_id:
            return Response({'error': 'Subcategory ID is required.'}, status=400)

        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({'error': 'Invalid subcategory ID.'}, status=400)

        product = Product.objects.create(
            product_name=data.get('product_name'),
            product_price=data.get('product_price'),
            product_description=data.get('product_description'),
            color=data.get('color'),
            material=data.get('material'),
            stock=data.get('stock'),
            subcategory=subcategory,
            category=subcategory.category, 
            user=request.user
        )

        for image in images:
            ProductImage.objects.create(product=product, image=image)

        product_serializer = ProductSerializer(product, context={'request': request})
        return Response(product_serializer.data, status=201)




class OrderViewset(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        
        user = request.user

        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        shipping_address = request.data.get('shipping_address')
        payment_method = request.data.get('payment_method')
        delivery_date = request.data.get('delivery_date')

        if not shipping_address or not payment_method:
            return Response({'shipping_address and payment_method are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if product_id:
           
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

            quantity = int(quantity or 1)

            if product.stock < quantity:
                return Response({f'Not enough stock for {product.product_name}'},
                                status=status.HTTP_400_BAD_REQUEST)

            product.stock -= quantity
            product.save()

            order = Order.objects.create(
                user=user,
                product=product,
                price=product.product_price,
                quantity=quantity,
                shipping_address=shipping_address,
                payment_method=payment_method,
                delivery_date=delivery_date,
                status='confirmed'
            )

            serializer = OrderSerializer(order)
            return Response([serializer.data], status=status.HTTP_201_CREATED)

        else:
        
            cart_items = AddToCart.objects.filter(user=user)
            if not cart_items.exists():
                return Response({'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

            created_orders = []
            for item in cart_items:
                product = item.product
                item_quantity = item.quantity

                if product.stock < item_quantity:
                    return Response({f'Not enough stock for {product.product_name}'},
                                    status=status.HTTP_400_BAD_REQUEST)

                product.stock -= item_quantity
                product.save()

                order = Order.objects.create(
                    user=user,
                    product=product,
                    price=product.product_price,
                    quantity=item_quantity,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    delivery_date=delivery_date,
                    status='confirmed'
                )

                created_orders.append(order)

            cart_items.delete()
            serializer = OrderSerializer(created_orders, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReviewViewset(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


    def create(self, request, *args, **kwargs):
        review_text = request.data['review_text']
        rating = request.data['rating']
        product_id = request.data['product_id']

        # print(review_text,rating,product_id)

        review = Review.objects.create(
            product_id = product_id,
            user_id = request.user.id,
            review_text = review_text,
            rating = rating
        )

        review.save()

        s = ReviewSerializer(review)
        return Response(s.data,status=status.HTTP_201_CREATED)
    

    def list(self, request, *args, **kwargs):
        reviews = Review.objects.all()
        rvs = ReviewSerializer(reviews,many=True)
        return Response(rvs.data,status=status.HTTP_200_OK)

class AddToCartViewSet(ModelViewSet):
    queryset = AddToCart.objects.all()
    serializer_class = AddToCartSerializer

    def get_queryset(self):
        return AddToCart.objects.filter(user=self.request.user)


    def create(self, request, *args, **kwargs):
        data = request.data
        product_id = data.get('product')
        quantity = data.get('quantity', 1)
        user = request.user

        if AddToCart.objects.filter(product_id=product_id, user= user).exists():
           return Response({"Product already in cart."}, status=status.HTTP_400_BAD_REQUEST)
        
        product = Product.objects.get(id=product_id)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save(user=user)
        cart_items = AddToCart.objects.create(
            product = product,
            quantity = quantity,
            user = user
        )
        cart_items.save()

        serializer = self.get_serializer(cart_items)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




def homepage(request):
    categories = Category.objects.all() 
    
    return render(request, 'index.html', {'categories': categories, 'user': request.user})


def sub_category(request, id):
    category_instance = get_object_or_404(Category, id=id) 
    subcategories = SubCategory.objects.filter(category=category_instance) 
    return render(request, "subcategory.html", {'category': category_instance, 'subcategories': subcategories})


def product_list_page(request, subcategory_id):
    
    if not request.user.is_authenticated:
        return redirect('userlogin') 
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
   
    products = Product.objects.filter(subcategory=subcategory)
    
    page_number = request.GET.get("page")
    paginator = Paginator(products, 4)
    page_obj = paginator.get_page(page_number)

    return render(request, 'product_list.html', {
        'subcategory': subcategory,
        'products': products,
        'page_obj':page_obj
    })



def product_detail(request, product_id):
   
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)  
    

    images = product.images.first()  
    
    
    if request.user.is_authenticated:
        is_in_cart = AddToCart.objects.filter(user=request.user, product=product).exists()
    else:
        is_in_cart = False

    page_number = request.GET.get("page")
    paginator = Paginator(reviews,3)
    page_obj = paginator.get_page(page_number)

    average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    star_range = range(1, 6)
    
    if average_rating:
        average_rating = round(average_rating,1)
    else:
        average_rating = 0    

    return render(request, 'product_detail.html', {
        'product': product,
        'images': images,
        'is_in_cart': is_in_cart,
        'reviews' : reviews,
        'page_obj' : page_obj,
        'average_rating' : average_rating,
        'star_range' : star_range,
        
    })



def view_cart(request):
    if request.user.is_authenticated:
        cart_items = AddToCart.objects.filter(user=request.user)
                
        for item in cart_items:
            item.product_images = item.product.images.first() 
            item.total_price = item.product.product_price * item.quantity  

        
        total_amount = sum(item.total_price for item in cart_items)
       
        return render(request, 'cart.html', {'cart_items': cart_items, 'total_amount': total_amount})
    else:
        
        return redirect('userlogin')


def search_bar(request):
    query = request.GET.get('q', '') 
    
    data = Product.objects.none() 
    
    if query:
       
        data = Product.objects.filter(
            Q(product_name__icontains=query) 
            
        )   
    return render(request, 'search.html', {'products': data, 'query': query}) 




def Create_category(request):
    if request.method == "POST":
        cat_name = request.POST.get("cat_name")
        cat_image = request.FILES.get("cat_image")

        
        category_instance = Category.objects.create( 
            name=cat_name,
            image=cat_image,
            user=request.user
        )
        category_instance.save()
        return redirect("homepage")
    
    return render(request, "create_category.html")


def Edit_cat(request, id):
    category_instance = get_object_or_404(Category, id=id) 

    if request.method == "POST":
        category_instance.name = request.POST['cat_name']
        
        if "cat_image" in request.FILES:
            category_instance.image = request.FILES['cat_image']

        category_instance.save()
        return redirect('homepage')

    return render(request, 'edit_cat.html', {'category': category_instance})


def create_subcategory(request, id):
    category_instance = Category.objects.get(id=id) 

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        category_image = request.FILES.get("category_image")

        sub_category_instance = SubCategory.objects.create( 
            category=category_instance, 
            name=category_name, 
            image=category_image,
            user=request.user 
        )
        sub_category_instance.save()
        return redirect('homepage')    
    
    return render(request, 'create_sub_category.html', {'category': category_instance})



def edit_sub_cat(request, subcategory_id):
   
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == 'POST':
        
        subcategory.name = request.POST.get('name')
        category_id = request.POST.get('category')
        if category_id:
           
            category = get_object_or_404(Category, id=category_id)
            subcategory.category = category

        if 'image' in request.FILES:
            subcategory.image = request.FILES['image']

        if 'delete_image' in request.POST and subcategory.image:
            subcategory.image.delete()

        subcategory.save()
        return redirect("homepage")
    categories = Category.objects.all()

    return render(request, 'edit_sub_category.html', {
        'subcategory': subcategory,
        'categories': categories
    })

def delete_sub_category(request,subcategory_id):
    sub_category = SubCategory.objects.get(id=subcategory_id)
    
    if request.method == 'POST':
        sub_category.delete()

        return HttpResponseRedirect("/")
    return render(request,'delete_sub_cat.html',{"sub_category":sub_category})


def create_product(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id) 
    category = subcategory.category  
    
    if request.method == 'POST':
       
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_description = request.POST.get('product_description')
        color = request.POST.get('color')
        material = request.POST.get('material')
        stock = request.POST.get('stock')

        product = Product(
            product_name=product_name,
            product_price=product_price,
            product_description=product_description,
            color=color,
            material=material,
            stock=stock,
            subcategory=subcategory,  
            category=category, 
        )
        product.save()
       
        images = request.FILES.getlist('images')  
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return redirect('product_list_page', subcategory_id=subcategory_id)

    return render(request, 'create_product.html', {'subcategory_id': subcategory_id, 'subcategory': subcategory})


def Edit_product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        
        product.product_name = request.POST.get("product_name")
        product.product_price = request.POST.get("product_price")
        product.product_description = request.POST.get("product_description")
        product.color = request.POST.get("color")
        product.material = request.POST.get("material")
        product.stock = request.POST.get("stock")
        
       
        delete_images = request.POST.getlist("delete_images") 
        for image_id in delete_images:
            image = get_object_or_404(ProductImage, id=image_id)
            image.delete()

       
        for image_id in product.images.all():
            new_image = request.FILES.get(f"new_image_{image_id.id}")
            if new_image:
               
                image_id.image = new_image
                image_id.save()

       
        new_images = request.FILES.getlist("new_images")
        for new_image in new_images:
            ProductImage.objects.create(product=product, image=new_image)

        product.save()
        return redirect("product_detail", product_id=product.id)

    return render(request, 'edit_product_page.html', {'product': product})



def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity = int(request.POST.get('quantity', 1)) 

    if product.stock == 0:
        return HttpResponse("this product is out of stock")

    if quantity > product.stock:
        
        return HttpResponse(f"Only {product.stock} items are available.")

   
    cart_item, created = AddToCart.objects.get_or_create(user=request.user, product=product)

    if not created:
        
        cart_item.quantity += quantity
    else:
      
        cart_item.quantity = quantity
    
   
    cart_item.save()
    return redirect('cart') 



def remove_from_cart(request, product_id):

    if not request.user.is_authenticated:
        return redirect('userlogin')
    
    cart_item = AddToCart.objects.filter(user=request.user, product_id=product_id).first()
    
    if cart_item:

        cart_item.delete()
    return redirect('cart')


def proceed_order(request):
    cart_items = AddToCart.objects.filter(user=request.user)
    
    if not cart_items:
        return HttpResponse("Your cart is empty.")

    total_amount = 0
    for item in cart_items:
        product = item.product
        quantity = item.quantity
        total_amount += product.product_price * quantity
        item.total_price = product.product_price * quantity  

    if request.method == "POST":
        for item in cart_items:
            product = item.product
            quantity = item.quantity

            if product.stock >= quantity:
              
                product.stock -= quantity
                product.save()

                
                delivery_date = request.POST.get('delivery_date')
                order = Order.objects.create(
                    user=request.user,
                    product=product,
                    price=product.product_price,
                    quantity=quantity,
                    shipping_address=request.POST.get('shipping_address'),
                    payment_method=request.POST.get('payment_method'),
                    delivery_date=delivery_date,
                    status='confirmed'
                )
                order.save()

      
        cart_items.delete()


        return redirect('order_confirmation', order_id=order.id)
        
    
    return render(request, 'proceed_order.html', {'cart_items': cart_items, 'total_amount': total_amount})


def Buy_Now(request, product_id):
    if not request.user.is_authenticated:
        return redirect('userlogin')

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        return HttpResponse("This product is out of stock.")

    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1)) 
        if quantity > product.stock:
            return HttpResponse("Not enough stock available.")

        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')
        delivery_date = request.POST.get('delivery_date', timezone.now() + timezone.timedelta(days=7))

        
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            price=product.product_price,
            shipping_address=shipping_address,
            payment_method=payment_method,
            delivery_date=delivery_date,
            status='confirmed'
        )

       
        product.stock -= quantity
        product.save()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'proceed_order.html', {
        'product': product,
        'is_buy_now': True  
    })

def order_confirmation(request,order_id):

    order = get_object_or_404(Order, id=order_id)
 
    total_price = order.quantity * order.price 
    return render(request,"order_confirm.html",{'order':order, 
    'total_proce':total_price,
    'delivery_date':order.delivery_date})


def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-booking_date')

   
    for order in orders:
        order.total_price = order.quantity * order.price
        order.is_delivered = order.delivery_date <= date.today()  

    paginator = Paginator(orders, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'order_history.html', {'page_obj': page_obj})




def cancel_order(request,order_id):
    
    if not request.user.is_authenticated:
        return redirect('userlogin')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'cancelled':
        return HttpResponse('this order has been cancelled')

    order.status = 'cancelled' 
    order.save()

    product = order.product
    product.stock += order.quantity
    product.save()

    return HttpResponse('Your order has been successfully canceled.') 


def add_review(request, product_id):
    if request.method == 'POST':
        
        product = get_object_or_404(Product, id=product_id)

        rating = request.POST.get('rating')
        review_text = request.POST.get("review_text")

       
        if rating is None or not rating.isdigit() or int(rating) not in range(1, 6):
            return HttpResponse("Invalid rating.")

       
        if not review_text or len(review_text.strip()) == 0:
            return HttpResponse("Review not availaible")

      
        review = Review(
            product=product,
            user=request.user,
            rating=int(rating),
            review_text=review_text,
        )
        review.save()
        
        
        return redirect('product_detail', product_id=product.id)

   
    product = get_object_or_404(Product, id=product_id)
    return render(request, "add_review.html", {'product': product})


def edit_review(request,product_id,review_id):

    product = get_object_or_404(Product, id = product_id)
    review = get_object_or_404(Review, id = review_id, user=request.user)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
         
        if rating is None or not rating.isdigit() or int(rating) not in range(1, 6):
            return HttpResponse("Invalid rating.")

        if not review_text or len(review_text.strip()) == 0:
            return HttpResponse("Review not available.")
        
        review.rating = int(rating)
        review.review_text = review_text
        review.save()

        
        return redirect('product_detail', product_id=product.id)

    return render(request, "add_review.html", {'product': product, 'review': review})


def delete_review(request,product_id, review_id):

    product = get_object_or_404(Product, id=product_id)

    review = get_object_or_404(Review,id = review_id, product_id = product_id, user = request.user)
    review.delete()
    return redirect('product_detail', product_id=product_id)



def mark_as_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_date <= date.today() and order.status != 'delivered':
       
        order.status = 'delivered'
        order.delivered_date = timezone.now()  
        order.save()
        is_delivered = True
        is_delivered_order_id = order.id
    else:
        is_delivered = False
        is_delivered_order_id = order.id

    return render(request, "order_history.html", {
        'order': order,
        'is_delivered': is_delivered,
        'is_delivered_order_id':is_delivered_order_id,
    })





def delete_product(request,product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        product.delete()

        return HttpResponseRedirect("/")
    return render(request,'delete_product.html',{"product":product})



def userlogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
          
            return render(request, "userlogin.html")

    return render(request, "userlogin.html")


def userlogout(request):
    logout(request)
    return redirect('homepage')


def createuser(request):
    if request.method == "POST":

        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        email = request.POST['email']
        phone_no = request.POST['phone_number']
        is_vendor = request.POST['is_vendor' ]
        # profile_img = request.FILES['image']

        if User.objects.filter(username=username).exists():
            return HttpResponse("Error: Username already exists. Please enter another username.")
        
    

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(password)
        user.save()

        profile = Profile.objects.create(
            phone_no = phone_no,
            is_vendor = is_vendor,
            # image = profile_img,
            user = user

        )
        profile.save()

       
        return redirect('userlogin')
    return render(request, "createuser.html")


class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer    
    





