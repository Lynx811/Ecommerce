from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Register View: Handles user registration
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Added request.FILES to handle file uploads
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')  # Redirect to the home page after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login View: Handles user login
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# User Profile View: Displays user's profile details
def user_profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

# Logout View: Logs the user out and redirects to home page
def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to homepage after logout

# Edit Profile View: Allows user to update profile details
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        # If password is not being changed, just save the user profile changes
        if user_form.is_valid():
            user_form.save()

        # If password is being changed, save the password change
        if password_form.is_valid():
            password_form.save()

        return redirect('profile')  # Redirect back to profile after updating
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'users/edit_profile.html', {'user_form': user_form, 'password_form': password_form})
