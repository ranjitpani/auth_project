from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Country, State, District, Block,Village,
    Store, Product, ProductStock, ProductImage,
    Category, StoreCategory,
    Order, OrderItem, ReturnRequest, RefundRequest, ExchangeRequest,SubCategory    # ✅ ADD
    
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
admin.site.register(SubCategory)
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
        'name', 'store', 'category','subcategory','is_latest',
        'price', 'discounted_price', 'is_available','delivery_charge','rating','gst_rate','gst_number'
    )
    list_filter = ('store', 'category','subcategory','is_latest', 'is_available','gst_rate')
    search_fields = ('name','gst_number')
    inlines = [ProductStockInline, ProductImageInline, ]

    fieldsets = (
        ('Basic Info', {'fields': ('name','store','category','subcategory','is_available','is_latest',)}),
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
    list_display = ('name','store_category','icon')
    list_filter = ('store_category',)
    search_fields = ('name',)

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

# ================== Orders ==================
# ================== Orders ==================
# from django.utils.html import format_html

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ('product_image',)

#     def product_image(self, obj):
#         """
#         Show the product image in admin. If product is deleted,
#         try to show the image from OrderItem itself.
#         """
#         if obj.product and obj.product.image:
#             return format_html('<img src="{}" width="50" />', obj.product.image.url)
#         elif hasattr(obj, 'product_image') and obj.product_image:
#             return format_html('<img src="{}" width="50" />', obj.product_image.url)
#         return "No Image"

#     product_image.short_description = "Product Image"
from django.utils.html import format_html
from django.contrib import admin
from .models import OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_image_preview',)

    def product_image_preview(self, obj):
        # ✅ Use snapshot first
        if obj.product_image:
            return format_html(
                '<img src="{}" width="80" style="border:1px solid #ccc; padding:4px;" />',
                obj.product_image
            )
        # Fallback if product still exists
        if obj.product and obj.product.image and getattr(obj.product.image, 'public_id', None):
            return format_html(
                '<img src="{}" width="80" style="border:1px solid #ccc; padding:4px;" />',
                obj.product.image.url
            )
        return "No Image"

    product_image_preview.short_description = "Product Image"
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_uid",
        "user",
        "delivery_boy", 
        "return_type",
        "total_amount",
        "payment_method",
        "status",
        "expected_delivery",
        "bus_partner",
        "delivery_state",
        "delivery_district",
        "delivery_block",
        "view_location",
        "created_at",
    )
    list_filter = ("status", "payment_method","delivery_boy","delivery_state",
        "delivery_district",
        "delivery_block","bus_partner","return_type",)
    list_editable = ("status", "expected_delivery","delivery_boy","return_type",)
    search_fields = ("order_uid", "user__email","delivery_boy__email")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    readonly_fields = ("order_uid",)
    def delivery_state(self, obj):
    # show from Order first, else from user profile
        return obj.delivery_state or (obj.user.state.name if obj.user.state else "—")

    def delivery_district(self, obj):
        return obj.delivery_district or (obj.user.district.name if obj.user.district else "—")

    def delivery_block(self, obj):
        return obj.delivery_block or (obj.user.block.name if obj.user.block else "—")

    delivery_state.short_description = "State"
    delivery_district.short_description = "District"
    delivery_block.short_description = "Block"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_boy":
            kwargs["queryset"] = CustomUser.objects.filter(is_delivery_boy=True)

        if db_field.name == "bus_partner":   # ✅ ADD
            kwargs["queryset"] = CustomUser.objects.filter(is_bus_partner=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def view_location(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://www.google.com/maps?q={},{}" target="_blank">'
                '📍 View Map</a>',
                obj.latitude,
                obj.longitude
            )
        return "—"

    view_location.short_description = "Customer Location"

    def save_model(self, request, obj, form, change):

    # ✅ Delivery Boy Assign
        if obj.delivery_boy and obj.status == "pending":
            obj.status = "assigned"

            if obj.return_type == "normal":
                obj.generate_otp()

        # ✅ Bus Partner Assign (NEW LOGIC)
        if obj.bus_partner and obj.status == "pending":
            obj.status = "bus_assigned"

        super().save_model(request, obj, form, change)

@admin.register(OrderItem)
class OrderItemRequestAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'order', 'get_user', 'return_requested', 'category_name',
        'refund_requested', 'exchange_requested', 'request_status','store_name'
    )
    list_filter = ('return_requested', 'refund_requested', 'exchange_requested', 'request_status')
    search_fields = ('product__name','store_name', 'order__order_uid', 'order__user__email')

    def get_user(self, obj):
        return obj.order.user
    get_user.short_description = 'User'

    
from django.contrib import admin

class OrderItemRequestBaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'get_user', 'request_status','store_name','category_name')
    search_fields = ('product__name','store_name', 'order__order_uid', 'order__user__email')

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
    
from django.contrib import admin
from .models import Offer, Product

class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'start_date', 'end_date', 'is_active')
    filter_horizontal = ('products',)  # 🔹 Makes multi-select easier in admin

admin.site.register(Offer, OfferAdmin)

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',)


from .models import BankAccount

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_holder", "bank_name", "account_number", "ifsc", "created_at")
    search_fields = ("user__email", "account_holder", "account_number", "ifsc")
