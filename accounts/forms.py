from django import forms
from .models import CustomUser, Country, State, District, Block

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['first_name', 'country', 'state', 'district', 'block']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['state'].queryset = State.objects.none()
#         self.fields['district'].queryset = District.objects.none()
#         self.fields['block'].queryset = Block.objects.none()

#         if 'country' in self.data:
#             try:
#                 country_id = int(self.data.get('country'))
#                 self.fields['state'].queryset = State.objects.filter(country_id=country_id)
#             except (ValueError, TypeError):
#                 pass
#         elif self.instance.pk and self.instance.country:
#             self.fields['state'].queryset = State.objects.filter(country=self.instance.country)

#         if 'state' in self.data:
#             try:
#                 state_id = int(self.data.get('state'))
#                 self.fields['district'].queryset = District.objects.filter(state_id=state_id)
#             except (ValueError, TypeError):
#                 pass
#         elif self.instance.pk and self.instance.state:
#             self.fields['district'].queryset = District.objects.filter(state=self.instance.state)

#         if 'district' in self.data:
#             try:
#                 district_id = int(self.data.get('district'))
#                 self.fields['block'].queryset = Block.objects.filter(district_id=district_id)
#             except (ValueError, TypeError):
#                 pass
#         elif self.instance.pk and self.instance.district:
#             self.fields['block'].queryset = Block.objects.filter(district=self.instance.district)
# forms.py
from django import forms
from .models import CustomUser, State, District, Block

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['first_name', 'country', 'state', 'district', 'block']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields['state'].queryset = State.objects.none()
#         self.fields['district'].queryset = District.objects.none()
#         self.fields['block'].queryset = Block.objects.none()

#         # ===== AJAX DATA =====
#         if 'country' in self.data:
#             self.fields['state'].queryset = State.objects.filter(
#                 country_id=self.data.get('country')
#             )

#         if 'state' in self.data:
#             self.fields['district'].queryset = District.objects.filter(
#                 state_id=self.data.get('state')
#             )

#         if 'district' in self.data:
#             self.fields['block'].queryset = Block.objects.filter(
#                 district_id=self.data.get('district')
#             )

#         # ===== EXISTING USER DATA =====
#         if self.instance.pk:
#             if self.instance.country:
#                 self.fields['state'].queryset = State.objects.filter(
#                     country=self.instance.country
#                 )
#             if self.instance.state:
#                 self.fields['district'].queryset = District.objects.filter(
#                     state=self.instance.state
#                 )
#             if self.instance.district:
#                 self.fields['block'].queryset = Block.objects.filter(
#                     district=self.instance.district
#                 )

from django import forms
from .models import CustomUser, Country, State, District, Block
from .models import OrderItem

# =========================
# PROFILE FORM (FIXED)
# =========================
from django import forms
from .models import CustomUser, Country, State, District, Block, Village

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'country', 'state', 'district', 'block', 'village']

    village = forms.ModelChoiceField(
        queryset=Village.objects.none(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # reset dropdowns
        self.fields['state'].queryset = State.objects.none()
        self.fields['district'].queryset = District.objects.none()
        self.fields['block'].queryset = Block.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        # ===== POST / AJAX DATA =====
        if self.data.get('country'):
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id)
            except:
                pass

        if self.data.get('state'):
            try:
                state_id = int(self.data.get('state'))
                self.fields['district'].queryset = District.objects.filter(state_id=state_id)
            except:
                pass

        if self.data.get('district'):
            try:
                district_id = int(self.data.get('district'))
                self.fields['block'].queryset = Block.objects.filter(district_id=district_id)
            except:
                pass

        # ✅ THIS PART WAS MISSING (BLOCK → VILLAGE)
        if self.data.get('block'):
            try:
                block_id = int(self.data.get('block'))
                self.fields['village'].queryset = Village.objects.filter(block_id=block_id)
            except:
                pass

        # ===== EDIT MODE (Existing User) =====
        if self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = State.objects.filter(country=self.instance.country)

            if self.instance.state:
                self.fields['district'].queryset = District.objects.filter(state=self.instance.state)

            if self.instance.district:
                self.fields['block'].queryset = Block.objects.filter(district=self.instance.district)

            if self.instance.block:
                self.fields['village'].queryset = Village.objects.filter(block=self.instance.block)




from django import forms
from .models import OrderItem

class OrderItemRequestForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            'request_reason',
            'image1', 'image2', 'image3',
            'refund_method',
            'upi_id',
            'bank_name',
            'bank_account_number',
            'bank_ifsc',
        ]

    def clean(self):
        cleaned_data = super().clean()

        reason = cleaned_data.get('request_reason')
        img1 = cleaned_data.get('image1')
        img2 = cleaned_data.get('image2')
        img3 = cleaned_data.get('image3')

        refund_method = cleaned_data.get('refund_method')
        upi_id = cleaned_data.get('upi_id')
        bank_name = cleaned_data.get('bank_name')
        bank_acc = cleaned_data.get('bank_account_number')
        bank_ifsc = cleaned_data.get('bank_ifsc')

        # ===== Common validation =====
        if not reason:
            raise forms.ValidationError("Reason is required")

        if not (img1 and img2 and img3):
            raise forms.ValidationError("3 images are mandatory")

        # ===== Payment validation (Return + Refund) =====
        if refund_method:
            if refund_method == 'upi' and not upi_id:
                raise forms.ValidationError("UPI ID is required")

            if refund_method == 'bank':
                if not all([bank_name, bank_acc, bank_ifsc]):
                    raise forms.ValidationError("Complete bank details required")

        return cleaned_data