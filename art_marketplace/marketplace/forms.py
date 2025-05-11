from django import forms
from .models import Artwork, UserProfile, WithdrawalRequest
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm, LoginForm

class UserRegistrationForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}), label='First Name')
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), label='Last Name')
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}), label='Username')
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}), label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Repeat password'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone', 'location', 'website', 'instagram', 'facebook', 'twitter']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1 (234) 567-8900'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://your-website.com'}),
            'instagram': forms.TextInput(attrs={'placeholder': '@username'}),
            'facebook': forms.TextInput(attrs={'placeholder': 'facebook.com/username'}),
            'twitter': forms.TextInput(attrs={'placeholder': '@username'}),
        }

class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'price', 'image', 'category', 'dimensions', 'materials']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ArtworkSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search')
    category = forms.CharField(required=False, label='Category')
    min_price = forms.DecimalField(required=False, label='Min Price')
    max_price = forms.DecimalField(required=False, label='Max Price')

class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'method', 'payment_details']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 1, 'step': 0.01}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'payment_details': forms.TextInput(attrs={'placeholder': 'Enter card number or PayPal email'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        profile = UserProfile.objects.get(user=self.user)
        if amount > profile.balance:
            raise forms.ValidationError("Insufficient balance.")
        return amount

class CustomAuthForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = 'Username'
        self.fields['password'].label = 'Password'
        self.fields['login'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})

    def login(self, request, redirect_url=None):
        return super().login(request, redirect_url) 