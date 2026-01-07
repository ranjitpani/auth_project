# from django import forms
# from django.forms import inlineformset_factory
# from accounts.models import Store, Product, ProductStock, Category
# from accounts.models import Product, ProductImage
# class StoreForm(forms.ModelForm):
#     class Meta:
#         model = Store
#         fields = [
#             "name", "image", "details", "country", "state", "district",
#             "block", "village", "category", "gst_number","latitude", "longitude" , "is_active"
#         ]
#         widgets = {
#             "name": forms.TextInput(attrs={"class": "form-control"}),
#             "latitude": forms.NumberInput(attrs={"step": "0.000001", "id": "id_latitude", "class": "form-control"}),
#             "longitude": forms.NumberInput(attrs={"step": "0.000001", "id": "id_longitude", "class": "form-control"}),
#             "details": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
#             "country": forms.Select(attrs={"class": "form-select"}),
#             "state": forms.Select(attrs={"class": "form-select"}),
#             "district": forms.Select(attrs={"class": "form-select"}),
#             "block": forms.Select(attrs={"class": "form-select"}),
#             "village": forms.Select(attrs={"class": "form-select"}),
#             "category": forms.Select(attrs={"class": "form-select"}),
#             "gst_number": forms.TextInput(attrs={"class": "form-control"}),
#             "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
#         }

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = [
#             "store", "name", "category", "price", "discounted_price",
#             "delivery_charge", "gst_rate", "gst_number", "description", "image",
#             "is_available"
#         ]
#         widgets = {
#             "store": forms.Select(attrs={"class": "form-select"}),
#             "name": forms.TextInput(attrs={"class": "form-control"}),
#             "category": forms.Select(attrs={"class": "form-select"}),
#             "price": forms.NumberInput(attrs={"class": "form-control"}),
#             "discounted_price": forms.NumberInput(attrs={"class": "form-control"}),
#             "delivery_charge": forms.NumberInput(attrs={"class": "form-control"}),
#             "gst_rate": forms.NumberInput(attrs={"class": "form-control"}),
#             "gst_number": forms.TextInput(attrs={"class": "form-control"}),
#             "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
#             "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
#         }

# class ProductStockForm(forms.ModelForm):
#     class Meta:
#         model = ProductStock
#         fields = ['size', 'stock']
#         widgets = {
#             'size': forms.TextInput(attrs={'class': 'form-control'}),
#             'stock': forms.NumberInput(attrs={'class': 'form-control'}),
#         }

# ProductStockFormSet = inlineformset_factory(
#     Product,
#     ProductStock,
#     form=ProductStockForm,
#     extra=1,
#     can_delete=True
# )

# class ProductImageForm(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ["image"]
#         widgets = {
#             "image": forms.ClearableFileInput(
#                 attrs={
#                     "class": "form-control",
#                     "multiple": True   # 🔥 KEY LINE
#                 }
#             )
#         }


# ProductImageFormSet = inlineformset_factory(
#     Product,
#     ProductImage,
#     form=ProductImageForm,
#     extra=1,
#     can_delete=True
# )
from django import forms
from django.forms import inlineformset_factory
from accounts.models import Store, Product, ProductStock, ProductImage


# ------------------------
# Store Form
# ------------------------
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            "name", "image", "details", "country", "state", "district",
            "block", "village", "category", "gst_number",
            "latitude", "longitude", "is_active"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "class": "form-control"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "state": forms.Select(attrs={"class": "form-select"}),
            "district": forms.Select(attrs={"class": "form-select"}),
            "block": forms.Select(attrs={"class": "form-select"}),
            "village": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "gst_number": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ------------------------
# Product Form (main product)
# ------------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "store", "name", "category", "price", "discounted_price",
            "delivery_charge", "gst_rate", "gst_number",
            "description", "image", "is_available"
        ]
        widgets = {
            "store": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "discounted_price": forms.NumberInput(attrs={"class": "form-control"}),
            "delivery_charge": forms.NumberInput(attrs={"class": "form-control"}),
            "gst_rate": forms.NumberInput(attrs={"class": "form-control"}),
            "gst_number": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ------------------------
# Product Stock (Size wise)
# ------------------------
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ["size", "stock"]
        widgets = {
            "size": forms.TextInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
        }


ProductStockFormSet = inlineformset_factory(
    Product,
    ProductStock,
    form=ProductStockForm,
    extra=1,
    can_delete=True
)


# ------------------------
# Product Image (MULTIPLE via formset)
# ------------------------
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image"]
        widgets = {
            # 🔥 NO multiple=True here
            "image": forms.FileInput(attrs={"class": "form-control"})
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,          # 🔥 ekathare 3 image add
    can_delete=True
)