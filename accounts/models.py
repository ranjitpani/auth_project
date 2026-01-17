from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from cloudinary.models import CloudinaryField
from django.conf import settings
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
    village = models.ForeignKey('Village', on_delete=models.SET_NULL, null=True, blank=True)
    is_store_owner = models.BooleanField(default=False)
    is_delivery_boy = models.BooleanField(default=False)
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
    
class Village(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name    
    
# ---------------------------
# Store Category Model
# ---------------------------
class StoreCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = CloudinaryField('icon', blank=True, null=True)
    icon_url = models.URLField(null=True, blank=True) 
    def __str__(self):
        return self.name    

# ---------------------------
# Store Model
# ---------------------------
class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_stores",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    image = CloudinaryField('image', blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(StoreCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='stores')
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
from decimal import Decimal
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
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        help_text="Rating out of 5 (eg: 4.5)"
    )
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00")
    )
    gst_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    # image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # local
    image = CloudinaryField('image', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def discount_percentage(self):
        if self.discounted_price and self.price:
            return round((self.price - self.discounted_price) / self.price * 100, 2)
        return 0

    def __str__(self):
        return self.name

# Optional: Size-wise stock management
# class ProductStock(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
#     size = models.CharField(max_length=50)  # e.g., S, M, L, XL
#     stock = models.PositiveIntegerField(default=0)  # Quantity available
#     def __str__(self):
#         return f"{self.product.name} - {self.size} ({self.stock})"
    
from django.utils.text import slugify

class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    size = models.CharField(max_length=50)  # e.g., S, M, L, XL
    stock = models.PositiveIntegerField(default=0)  # Quantity available
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate SKU if not already set
        if not self.sku:
            # Take first 10 letters of product name + first 5 letters of size
            product_code = slugify(self.product.name)[:10]
            size_code = slugify(self.size)[:5]
            base_sku = f"{product_code}-{size_code}"

            # Ensure uniqueness
            existing = ProductStock.objects.filter(sku=base_sku)
            counter = 1
            sku_final = base_sku
            while existing.exists():
                sku_final = f"{base_sku}-{counter}"
                existing = ProductStock.objects.filter(sku=sku_final)
                counter += 1

            self.sku = sku_final

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.sku})"    
# ---------------------------
# Product Images (Multiple per product)
# ---------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', blank=True, null=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 Auto set first image as product thumbnail
        if not self.product.image:
            self.product.image = self.image
            self.product.save()

    def __str__(self):
        return f"{self.product.name} image"
    

# models.py
from django.conf import settings
from django.db import models
class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    alt_mobile = models.CharField(max_length=15, blank=True)

    pincode = models.CharField(max_length=6)

    state = models.CharField(max_length=100, default="", blank=True)
    district = models.CharField(max_length=100, default="", blank=True)
    block = models.CharField(max_length=100, default="", blank=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    room_no = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField()
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_default = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.pincode}"
    

import uuid
from django.utils import timezone
from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("packed", "Packed"),
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("picked_up", "Picked Up"), 
        ("rejected", "Rejected"),
        ("out_for_delivery", "Out For Delivery"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
        ("refunded", "Refunded"),
        ("exchanged", "Exchanged"),
    )
    RETURN_TYPE_CHOICES = (
    ("normal", "Normal Delivery"),
    ("return", "Return Pickup"),
    ("refund", "Refund Pickup"),
    ("exchange", "Exchange Pickup"),
)

    return_type = models.CharField(
    max_length=20,
    choices=RETURN_TYPE_CHOICES,
    default="normal"
)

    PAYMENT_CHOICES = (
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('cod', 'Cash on Delivery'),
    )

    # 🔥 UNIQUE ORDER ID
    order_uid = models.CharField(
        max_length=25,
        null=True,      # ✅ VERY IMPORTANT
        blank=True,
        unique=True,
        editable=False,
        db_index=True
    )
    
    delivery_boy = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="delivery_orders"
)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    expected_delivery = models.DateField(null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    delivery_name = models.CharField(max_length=200, blank=True, null=True)
    delivery_phone = models.CharField(max_length=15, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    delivery_city = models.CharField(max_length=100, blank=True, null=True)
    delivery_postal_code = models.CharField(max_length=10, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_uid:
            self.order_uid = self.generate_order_uid()
        super().save(*args, **kwargs)

    def generate_order_uid(self):
        date_str = timezone.now().strftime("%Y%m%d")
        rand = uuid.uuid4().hex[:4].upper()
        return f"ORD-{date_str}-{rand}"

    def __str__(self):
        return self.order_uid
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.delivery_otp = str(random.randint(100000, 999999))
        self.save()
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    category_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    size = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    product_image = models.URLField(blank=True, null=True)
    
    # ======================
    # GST Details (Snapshot)
    # ======================
    gst_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Seller GSTIN number"
    )
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="GST percentage like 5, 12, 18"
    )

    # =====================
    # Request Flags
    # =====================
    return_requested = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    exchange_requested = models.BooleanField(default=False)
    request_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ),
        default='pending'
    )
    request_date = models.DateField(null=True, blank=True)
    processed_date = models.DateField(null=True, blank=True)

    # =====================
    # Request Details
    # =====================
    request_reason = models.TextField(blank=True, null=True)
    # image1 = models.ImageField(upload_to='order_requests/', blank=True, null=True)
    # image2 = models.ImageField(upload_to='order_requests/', blank=True, null=True)
    # image3 = models.ImageField(upload_to='order_requests/', blank=True, null=True)
    image1 = CloudinaryField('image1', blank=True, null=True)
    image2 = CloudinaryField('image2', blank=True, null=True)
    image3 = CloudinaryField('image3', blank=True, null=True)

    # =====================
    # Payment Details (USED FOR RETURN + REFUND)
    # =====================
    refund_method = models.CharField(
        max_length=10,
        choices=(('upi', 'UPI'), ('bank', 'Bank')),
        blank=True,
        null=True
    )
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    product_sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Snapshot of product SKU at time of order"
    )
    def save(self, *args, **kwargs):
        if self.product:
            if not self.product_name:
                self.product_name = self.product.name

            if not self.store_name and self.product.store:
                self.store_name = self.product.store.name

            if not self.category_name and self.product.category:
                self.category_name = self.product.category.name

            if not self.product_sku:
                try:
                    stock = self.product.stocks.first()
                    self.product_sku = stock.sku if stock else None
                except Exception:
                    self.product_sku = None

            # 🔥 IMAGE SNAPSHOT (SAFE)
            if not self.product_image:
                try:
                    if self.product.image:
                        self.product_image = self.product.image.url
                except Exception:
                    self.product_image = None

        super().save(*args, **kwargs)
    # =====================
    # GST Calculation
    # =====================
    def gst_amount(self):
        """Returns GST amount for this order item."""
        return (self.price * self.quantity * self.gst_rate) / 100

    # =====================
    # Total Price with GST
    # =====================
    def total_with_gst(self):
        """Returns total price including GST for this order item."""
        return (self.price * self.quantity) + self.gst_amount()

    def __str__(self):
        return f"{self.product_name or 'Deleted Product'} × {self.quantity}"

class Seller(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    return_policy = models.TextField(default="No returns/refunds after 7 days")


class ReturnRequest(OrderItem):
    class Meta:
        proxy = True
        verbose_name = "Return Request"
        verbose_name_plural = "Return Requests"

class RefundRequest(OrderItem):
    class Meta:
        proxy = True
        verbose_name = "Refund Request"
        verbose_name_plural = "Refund Requests"

class ExchangeRequest(OrderItem):
    class Meta:
        proxy = True
        verbose_name = "Exchange Request"
        verbose_name_plural = "Exchange Requests"  


from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
    
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user} - {self.otp}"

