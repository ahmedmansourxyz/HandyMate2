from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, ProviderAvailability

class ProviderAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ProviderAvailability
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Start time must be before end time.")
        return cleaned_data



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control',
        }),
        label="First Name"
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control',
        }),
        label="Last Name"
    )
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control',
        })
    )
    user_type = forms.ChoiceField(
        choices=(
            ('client', 'Client'),
            ('provider', 'Service Provider'),
        ),
        widget=forms.RadioSelect,
        label="Register as",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a unique username',
                'class': 'form-control',
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Create a password',
                'class': 'form-control',
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm your password',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'profile_image']
        labels = {
            'phone_number': 'Phone Number',
            'address': 'Address',
            'city': 'City',
            'profile_image': 'Profile Picture'
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_provider:
            self.fields['years_of_experience'] = forms.IntegerField(
                required=False,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                label='Years of Experience',
                initial=self.instance.years_of_experience
            )
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.instance and self.instance.is_provider:
            years = self.cleaned_data.get('years_of_experience')
            profile.years_of_experience = years if years is not None else (profile.years_of_experience or 0)
        if commit:
            profile.save()
        return profile