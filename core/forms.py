from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User,
    ResidentProfile,
    CollectorProfile,
    Business,
    WasteRequest,
    WasteReport,
    CollectionItem,
)


class ResidentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=255, required=False)
    location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "location",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.RESIDENT

        if commit:
            user.save()
            ResidentProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data["phone_number"],
                address=self.cleaned_data["address"],
                location=self.cleaned_data["location"],
            )

        return user


class CollectorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    business_name = forms.CharField(max_length=200, required=True)
    registration_number = forms.CharField(max_length=100, required=True)
    business_email = forms.EmailField(required=False)
    business_phone = forms.CharField(max_length=20, required=True)
    business_address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "business_name",
            "registration_number",
            "business_email",
            "business_phone",
            "business_address",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.COLLECTOR

        if commit:
            user.save()

            business = Business.objects.create(
                name=self.cleaned_data["business_name"],
                registration_number=self.cleaned_data["registration_number"],
                phone_number=self.cleaned_data["business_phone"],
                email=self.cleaned_data["business_email"],
                address=self.cleaned_data["business_address"],
            )

            CollectorProfile.objects.create(
                user=user,
                business=business,
                phone_number=self.cleaned_data["phone_number"],
            )

        return user

class WasteRequestForm(forms.ModelForm):
    class Meta:
        model = WasteRequest
        fields = (
            "category",
            "description",
            "location",
            "requested_date",
        )
        widgets = {
            "requested_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

class WasteReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = (
            "description",
            "location",
            "image",
        )
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe the waste problem..."
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "Where is the waste problem?"
                }
            ),
        }

class CollectionItemForm(forms.ModelForm):
    class Meta:
        model = CollectionItem
        fields = (
            "category",
            "quantity",
            "unit",
            "is_correctly_sorted",
        )