from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, help_text="Enter your phone number")
    profile_picture = forms.ImageField(required=False, help_text="Optional profile picture")
    location = forms.CharField(max_length=255, required=False, help_text="Enter your location (optional)")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'profile_picture', 'location']  # Added profile and location fields



from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']



from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(max_length=15, required=True, help_text="Update your phone number", initial="")
    profile_picture = forms.ImageField(required=False, help_text="Optional profile picture", initial="")
    location = forms.CharField(max_length=255, required=False, help_text="Update your location", initial="")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'profile_picture', 'location']  # Include profile and location for updates

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password-input'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password-input'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password-input'}))