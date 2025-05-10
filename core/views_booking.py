from formtools.wizard.views import SessionWizardView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import timedelta
from django.urls import reverse
from core.models import Job, Notification
from accounts.models import Profile
from core.booking_forms import TimeslotForm, TaskSelectionForm, ConfirmForm
from core.constants import TASKS_BY_CATEGORY
from django.utils import timezone

# For bookings without a preselected service
class BookingWizardWithoutService(SessionWizardView):
    form_list = [
        ('task', TaskSelectionForm),
        ('timeslot', TimeslotForm),
        ('confirm', ConfirmForm),
    ]
    templates = {
        "task": "core/booking_wizard_task.html",
        "timeslot": "core/booking_wizard_timeslot.html",
        "confirm": "core/booking_wizard_confirm.html",
    }

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.is_provider:
            messages.error(request, "Service providers cannot book services.")
            return redirect("provider_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        if step == "task":
            kwargs.update({
                "service_category": self.kwargs.get("service_category"),
                "provider": provider,
            })
        if step == "timeslot":
            kwargs.update({"provider": provider})
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        normalized_category = self.kwargs.get("service_category")
        available_weekdays = [av.day_of_week for av in provider.availabilities.all()]
        if self.steps.current == "timeslot":
            now = timezone.localtime(timezone.now())
            today_name = now.strftime("%A")
            today_availability = provider.availabilities.filter(day_of_week=today_name).first()
            if today_availability:
                provider_today_end = today_availability.end_time.strftime("%H:%M:%S")
            else:
                provider_today_end = ""
            context["provider_today_end"] = provider_today_end
        context.update({
            "provider": provider,
            "provider_first_name": provider.first_name or provider.user.first_name,
            "service_category": normalized_category,
            "available_weekdays": available_weekdays,
        })
        if self.steps.current == "confirm":
            timeslot_data = self.get_cleaned_data_for_step("timeslot") or {}
            task_data = self.get_cleaned_data_for_step("task") or {}
            task_code = task_data.get("task")
            human_task = task_code
            for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
                if code == task_code:
                    human_task = label
                    break
            service_obj = provider.service_set.filter(
                category__iexact=normalized_category,
                task=task_code,
                is_available=True
            ).first()
            if not service_obj:
                context['service_unavailable'] = True
                messages.error(self.request, "The service you are trying to book is currently not available.")
            else:
                context.update({
                    "timeslot_data": timeslot_data,
                    "task_data": {"task": human_task},
                    "price": service_obj.price_rate if service_obj.price_rate else "N/A",
                })
        return context

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        normalized_category = self.kwargs.get("service_category")
        task_code = data.get("task")
        human_task = task_code
        for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
            if code == task_code:
                human_task = label
                break
        service_obj = provider.service_set.filter(
            category__iexact=normalized_category,
            task=task_code,
            is_available=True
        ).first()
        if not service_obj:
            messages.error(self.request, "The service you are trying to book is currently not available.")
            return redirect("service_providers", category=normalized_category, task="all")
        additional_note = data.get("additional_note", "")
        job = Job.objects.create(
            client=self.request.user.profile,
            task=human_task,
            note=additional_note,
            category=normalized_category,
            scheduled_date=data.get("scheduled_date"),
            status=Job.PENDING_CONFIRMATION,
            payment_status="pending",
            duration=timedelta(hours=1),
            provider=provider,
            price_rate_snapshot=service_obj.price_rate
        )
        Notification.objects.create(
            user=provider,
            sender=job.client,
            message=f"You have a new booking request for '{job.task}' from {job.client.user.username}.",
            link=reverse('job_detail', args=[job.id])
        )
        messages.success(self.request, "Your booking request has been submitted and is awaiting confirmation.")
        self.storage.reset()
        return redirect("dashboard")
    
class BookingWizardWithService(SessionWizardView):
    form_list = [
        ('timeslot', TimeslotForm),
        ('confirm', ConfirmForm),
    ]
    templates = {
        "timeslot": "core/booking_wizard_timeslot.html",
        "confirm": "core/booking_wizard_confirm.html",
    }

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.is_provider:
            messages.error(request, "Service providers cannot book services.")
            return redirect("provider_dashboard")
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        normalized_category = self.kwargs.get("service_category")
        service_code = self.kwargs.get("service")
        service_obj = provider.service_set.filter(
            category__iexact=normalized_category,
            task=service_code,
            is_available=True
        ).first()
        if not service_obj:
            messages.error(request, "The service you are trying to book is currently not available.")
            return redirect("service_providers", category=normalized_category, task="all")
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        if step == "timeslot":
            kwargs.update({"provider": provider})
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        normalized_category = self.kwargs.get("service_category")
        available_weekdays = [av.day_of_week for av in provider.availabilities.all()]
        if self.steps.current == "timeslot":
            now = timezone.localtime(timezone.now())
            today_name = now.strftime("%A")
            today_availability = provider.availabilities.filter(day_of_week=today_name).first()
            if today_availability:
                provider_today_end = today_availability.end_time.strftime("%H:%M:%S")
            else:
                provider_today_end = ""
            context["provider_today_end"] = provider_today_end
        context.update({
            "provider": provider,
            "provider_first_name": provider.first_name or provider.user.first_name,
            "service_category": normalized_category,
            "available_weekdays": available_weekdays,
        })
        if self.steps.current == "confirm":
            timeslot_data = self.get_cleaned_data_for_step("timeslot") or {}
            service_code = self.kwargs.get("service")
            human_task = service_code
            for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
                if code == service_code:
                    human_task = label
                    break
            service_obj = provider.service_set.filter(
                category__iexact=normalized_category,
                task=service_code,
                is_available=True
            ).first()
            context.update({
                "timeslot_data": timeslot_data,
                "selected_task": human_task,
                "price": service_obj.price_rate if service_obj.price_rate else "N/A",
            })
        return context

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        provider = get_object_or_404(Profile, id=self.kwargs.get("provider_id"))
        normalized_category = self.kwargs.get("service_category")
        service_code = self.kwargs.get("service")
        human_task = service_code
        for code, label in TASKS_BY_CATEGORY.get(normalized_category, []):
            if code == service_code:
                human_task = label
                break
        service_obj = provider.service_set.filter(
            category__iexact=normalized_category,
            task=service_code,
            is_available=True
        ).first()
        if not service_obj:
            messages.error(self.request, "The service you are trying to book is currently not available.")
            return redirect("service_providers", category=normalized_category, task="all")
        additional_note = data.get("additional_note", "")
        job = Job.objects.create(
            client=self.request.user.profile,
            task=human_task,
            note=additional_note,
            category=normalized_category,
            scheduled_date=data.get("scheduled_date"),
            status=Job.PENDING_CONFIRMATION,
            payment_status="pending",
            duration=timedelta(hours=1),
            provider=provider,
            price_rate_snapshot=service_obj.price_rate
        )
        Notification.objects.create(
            user=provider,
            sender=job.client,
            message=f"You have a new booking request for '{job.task}' from {job.client.user.username}.",
            link=reverse('job_detail', args=[job.id])
        )
        messages.success(self.request, "Your booking request has been submitted and is awaiting confirmation.")
        self.storage.reset()
        return redirect("dashboard")
