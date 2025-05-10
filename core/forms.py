from django import forms
from .models import Job, ChatMessage
from .models import Service, Review
from django.core.exceptions import ValidationError
from datetime import timedelta

class ServiceAddForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'task', 'price_rate']
        labels = {
            'category': 'Service Category',
            'task': 'Service Task',
            'price_rate': 'Your Price Rate (EUR)',
        }
        widgets = {
            'category': forms.HiddenInput(),
            'task': forms.HiddenInput(),
            'price_rate': forms.NumberInput(attrs={
                'placeholder': 'Enter your price',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        task = cleaned_data.get('task')
        if self.provider and category and task:
            if Service.objects.filter(provider=self.provider, category=category, task=task).exists():
                raise ValidationError("You have already added this service.")
        return cleaned_data

    def clean_price_rate(self):
        price = self.cleaned_data.get('price_rate')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price



class JobDurationUpdateForm(forms.ModelForm):
    duration = forms.DurationField(
        label="New Duration (HH:MM:SS)",
        help_text="Enter the new duration for the job. Example: 01:00:00 for 1 hour.",
        initial=timedelta(hours=1)
    )

    class Meta:
        model = Job
        fields = ['duration']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        labels = {
            'message': 'Your Message',
        }
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Type your message here...',
                'class': 'form-control',
                'rows': 2,
            }),
        }
        error_messages = {
            'message': {
                'required': 'Please enter a message before sending.',
                'max_length': 'Your message is too long.',
            },
        }
    
    def clean_message(self):
        data = self.cleaned_data.get('message')
        if 'spam' in data.lower():
            raise forms.ValidationError("Your message contains prohibited content.")
        if len(data) > 1000:
            raise forms.ValidationError("Your message is too long.")
        return data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5, 
                'class': 'form-control',
                'placeholder': 'Enter a rating (1-5)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Leave an optional comment..'
            }),
        }