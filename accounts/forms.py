from django import forms
from .models import CustomUser, Country, State, District, Block

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'country', 'state', 'district', 'block']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].queryset = State.objects.none()
        self.fields['district'].queryset = District.objects.none()
        self.fields['block'].queryset = Block.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.country:
            self.fields['state'].queryset = State.objects.filter(country=self.instance.country)

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['district'].queryset = District.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.state:
            self.fields['district'].queryset = District.objects.filter(state=self.instance.state)

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['block'].queryset = Block.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.district:
            self.fields['block'].queryset = Block.objects.filter(district=self.instance.district)