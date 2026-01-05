from django import forms
from .models import (
    CustomUser,
    Country,
    State,
    District,
    Block,
    Village,
    OrderItem
)

# =========================
# PROFILE FORM (FINAL)
# =========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'country', 'state', 'district', 'block', 'village']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Empty by default
        self.fields['state'].queryset = State.objects.none()
        self.fields['district'].queryset = District.objects.none()
        self.fields['block'].queryset = Block.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        # -----------------------
        # AJAX DATA (NO SAVE)
        # -----------------------
        if self.data.get('country'):
            self.fields['state'].queryset = State.objects.filter(
                country_id=self.data.get('country')
            )

        if self.data.get('state'):
            self.fields['district'].queryset = District.objects.filter(
                state_id=self.data.get('state')
            )

        if self.data.get('district'):
            self.fields['block'].queryset = Block.objects.filter(
                district_id=self.data.get('district')
            )

        if self.data.get('block'):
            self.fields['village'].queryset = Village.objects.filter(
                block_id=self.data.get('block')
            )

        # -----------------------
        # EDIT MODE (Existing User)
        # -----------------------
        if self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = State.objects.filter(
                    country=self.instance.country
                )

            if self.instance.state:
                self.fields['district'].queryset = District.objects.filter(
                    state=self.instance.state
                )

            if self.instance.district:
                self.fields['block'].queryset = Block.objects.filter(
                    district=self.instance.district
                )

            if self.instance.block:
                self.fields['village'].queryset = Village.objects.filter(
                    block=self.instance.block
                )


# =========================
# ORDER ITEM REQUEST FORM
# =========================
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

        if not cleaned_data.get('request_reason'):
            raise forms.ValidationError("Reason is required")

        if not (
            cleaned_data.get('image1') and
            cleaned_data.get('image2') and
            cleaned_data.get('image3')
        ):
            raise forms.ValidationError("3 images are mandatory")

        refund_method = cleaned_data.get('refund_method')

        if refund_method == 'upi' and not cleaned_data.get('upi_id'):
            raise forms.ValidationError("UPI ID is required")

        if refund_method == 'bank':
            if not all([
                cleaned_data.get('bank_name'),
                cleaned_data.get('bank_account_number'),
                cleaned_data.get('bank_ifsc')
            ]):
                raise forms.ValidationError("Complete bank details required")

        return cleaned_data

