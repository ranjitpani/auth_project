from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Country, State, District, Block, Store, Product, ProductStock, ProductImage, Category,StoreCategory

# ------------------ CustomUser ------------------
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'country', 'state', 'district', 'block', 'is_staff', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'phone', 'country', 'state', 'district', 'block')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2', 'country', 'state', 'district', 'block', 'is_staff', 'is_verified')}
        ),
    )
    search_fields = ('email', 'first_name',)
    ordering = ('email',)
admin.site.register(CustomUser, CustomUserAdmin)

# ------------------ Location ------------------
admin.site.register(Country)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Block)

# ------------------ Store ------------------
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'state', 'district', 'block')
    list_filter = ('category', 'country', 'state', 'district', 'block')
    search_fields = ('name',)

admin.site.register(Store, StoreAdmin)

# ------------------ Product ------------------
class ProductStockInline(admin.TabularInline):
    model = ProductStock
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'category', 'price', 'discounted_price', 'is_available')
    list_filter = ('store', 'category', 'is_available')
    search_fields = ('name',)
    inlines = [ProductStockInline, ProductImageInline]

# ------------------ Category ------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)    