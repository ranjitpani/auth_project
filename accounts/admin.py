from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Country, State, District, Block,Village,
    Store, Product, ProductStock, ProductImage,
    Category, StoreCategory,
    Order, OrderItem, ReturnRequest, RefundRequest, ExchangeRequest     # ✅ ADD
    
)
import nested_admin

# ================== Custom User ==================
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'first_name', 'country', 'state',
        'district', 'block', 'is_staff', 'is_verified'
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'phone',
                'country', 'state', 'district', 'block'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_staff', 'is_active',
                'is_verified', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name',
                'password1', 'password2',
                'country', 'state', 'district', 'block',
                'is_staff', 'is_verified'
            )
        }),
    )

    search_fields = ('email', 'first_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

# ================== Location ==================
admin.site.register(Country)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Block)
admin.site.register(Village)

# ================== Store ==================
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'state', 'district', 'block','village')
    list_filter = ('category', 'country', 'state', 'district', 'block','village')
    search_fields = ('name',)

admin.site.register(Store, StoreAdmin)




# ---------------- Image Inline ----------------
class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 1

# ---------------- Stock Inline ----------------
class ProductStockInline(nested_admin.NestedTabularInline):
    model = ProductStock
    extra = 1


# ---------------- Product Admin ----------------
@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'name', 'store', 'category',
        'price', 'discounted_price', 'is_available','delivery_charge','rating','gst_rate','gst_number'
    )
    list_filter = ('store', 'category', 'is_available','gst_rate')
    search_fields = ('name','gst_number')
    inlines = [ProductStockInline, ProductImageInline, ]

    fieldsets = (
        ('Basic Info', {'fields': ('name','store','category','is_available')}),
        ('Pricing', {'fields': ('price','discounted_price','delivery_charge')}),
        ('GST Details', {'fields': ('gst_rate','gst_number')}),
        ('Rating', {'fields': ('rating',)}),
        ("Description", {
            "fields": ("description",)
        }),
    )




# ================== Category ==================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

# ================== Orders ==================
# ================== Orders ==================
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_image',)

    def product_image(self, obj):
        """
        Show the product image in admin. If product is deleted,
        try to show the image from OrderItem itself.
        """
        if obj.product and obj.product.image:
            return format_html('<img src="{}" width="50" />', obj.product.image.url)
        elif hasattr(obj, 'product_image') and obj.product_image:
            return format_html('<img src="{}" width="50" />', obj.product_image.url)
        return "No Image"

    product_image.short_description = "Product Image"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_amount",
        "payment_method",
        "status",
        "expected_delivery",
        "created_at",
    )
    list_filter = ("status", "payment_method")
    list_editable = ("status", "expected_delivery")
    search_fields = ("id", "user__email")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

@admin.register(OrderItem)
class OrderItemRequestAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'order', 'get_user', 'return_requested', 
        'refund_requested', 'exchange_requested', 'request_status'
    )
    list_filter = ('return_requested', 'refund_requested', 'exchange_requested', 'request_status')
    search_fields = ('product__name', 'order__id', 'order__user__email')

    def get_user(self, obj):
        return obj.order.user
    get_user.short_description = 'User'

from django.contrib import admin

class OrderItemRequestBaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'get_user', 'request_status')
    search_fields = ('product__name', 'order__id', 'order__user__email')

    def get_user(self, obj):
        return obj.order.user
    get_user.short_description = 'User'

@admin.register(ReturnRequest)
class ReturnRequestAdmin(OrderItemRequestBaseAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(return_requested=True)

@admin.register(RefundRequest)
class RefundRequestAdmin(OrderItemRequestBaseAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(refund_requested=True)

@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(OrderItemRequestBaseAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(exchange_requested=True)
    
    