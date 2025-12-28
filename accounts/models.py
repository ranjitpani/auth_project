from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# ---------------------------
# Custom User Manager
# ---------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ---------------------------
# Custom User
# ---------------------------
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ForeignKey('Block', on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ---------------------------
# Location Models
# ---------------------------
class Country(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Block(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
# ---------------------------
# Store Category Model
# ---------------------------
class StoreCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='store_category_icons/', blank=True, null=True)
    icon_url = models.URLField(null=True, blank=True) 
    def __str__(self):
        return self.name    

# ---------------------------
# Store Model
# ---------------------------
class Store(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='store_images/', null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    # category = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(
    StoreCategory,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='stores'
)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

# ---------------------------
# Category Model (for Products)
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# ---------------------------
# Product Model
# ---------------------------
# ---------------------------
# Product Model (Updated)
# ---------------------------
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        'Category',  # Link to Category model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # local
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def discount_percentage(self):
        if self.discounted_price and self.price:
            return round((self.price - self.discounted_price) / self.price * 100, 2)
        return 0

    def __str__(self):
        return self.name

# Optional: Size-wise stock management
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    size = models.CharField(max_length=50)  # e.g., S, M, L, XL
    stock = models.PositiveIntegerField(default=0)  # Quantity available
    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.stock})"
    
# ---------------------------
# Product Images (Multiple per product)
# ---------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/') 
    def __str__(self):
        return f"{self.product.name} Image"
    

# models.py
from django.conf import settings
from django.db import models

class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    alt_mobile = models.CharField(max_length=15, blank=True)
    pincode = models.CharField(max_length=10)
    address = models.TextField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.pincode}"    
    
   