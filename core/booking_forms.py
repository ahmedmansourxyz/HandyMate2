from django import forms
from datetime import timedelta
from django.utils import timezone
from core.models import Job
from core.constants import TASKS_BY_CATEGORY 

class TimeslotForm(forms.Form):
    scheduled_date = forms.DateTimeField(
        widget=forms.HiddenInput(attrs={'id': 'id_scheduled_date'}),
        label="Scheduled Date",
        input_formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]
    )

    def __init__(self, *args, **kwargs):
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if not scheduled_date:
            raise forms.ValidationError("Please select a valid time slot.")
        if timezone.is_naive(scheduled_date):
            scheduled_date = timezone.make_aware(scheduled_date, timezone.get_current_timezone())
        
        booking_duration = timedelta(hours=1)
        slot_end = scheduled_date + booking_duration
        
        overlapping_jobs = Job.objects.filter(
            provider=self.provider,
            scheduled_date__lt=slot_end,
            scheduled_date__gte=scheduled_date,
            status=Job.IN_PROGRESS
        )
        if overlapping_jobs.exists():
            raise forms.ValidationError("This time slot is already booked. Please choose another time.")
        return scheduled_date


class TaskSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        service_category = kwargs.pop('service_category')
        provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        normalized_category = service_category.capitalize()
        tasks = []
        if provider:
            provider_tasks = provider.service_set.filter(category__iexact=normalized_category)\
                                                 .values_list('task', flat=True).distinct()
            for task_code in provider_tasks:
                task_label = task_code  
                for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
                    if code == task_code:
                        task_label = label
                        break
                tasks.append((task_code, task_label))
        self.fields['task'] = forms.ChoiceField(
            choices=tasks,
            label="Select Service",
            widget=forms.HiddenInput(attrs={'id': 'id_task'})
        )

class ConfirmForm(forms.Form):
    additional_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Leave an optional note for the service provider...',
            'class': 'form-control',
            'rows': 3,
        }),
        label="Additional Notes"
    )
