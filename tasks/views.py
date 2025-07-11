import logging
import os

from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView
from django.db.models import Min, Max
from django.utils import timezone
from django.db import transaction
from django.utils.timezone import localdate
from django.conf import settings

from .models import Task, Attachment, MetricArchetype, Metric
from .forms import TaskForm
from .jobs import attachment_processing
logger = logging.getLogger(__name__)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task-list-today')  # Redirect to task list after creation

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the user to the logged-in user
        task = form.save()

        file = self.request.FILES.get('attachment')
        if file:
            attachment = Attachment.objects.create(task=task, image=file)
        if attachment:
            transaction.on_commit(lambda: attachment_processing(attachment))
        # placeholder for your job trigger
        return super().form_valid(form)

class TodayTasksListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list_today.html"
    context_object_name = "tasks"

    def get_queryset(self):
        # Get the local date for “today”
        today = timezone.localdate()
        # Filter only this user's tasks whose start_time is on that date
        return (
            Task.objects
                .filter(user=self.request.user, start_time__date=today)
                .order_by("start_time")
        )

class KneeMobilityView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/knee_mobility.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        left_arc = MetricArchetype.objects.get(slug="left_knee_angle")
        left_qs  = Metric.objects.filter(attachment__task__user=user,
                                         archetype=left_arc)
        healthy_min = left_qs.aggregate(Min("value"))["value__min"]
        healthy_max = left_qs.aggregate(Max("value"))["value__max"]
        total_span = healthy_max - healthy_min

        right_arc = MetricArchetype.objects.get(slug="right_knee_angle")
        right_qs = Metric.objects.filter(attachment__task__user=user,
                                         archetype=right_arc)
        weeks = {}

        # 3) Build ISO‐week buckets
        weeks = {}
        for m in right_qs:
          # group by the Task.start_time, not the upload time
          dt = m.attachment.task.start_time
          y, w, _ = dt.isocalendar()
          key     = (y, w)

          weeks.setdefault(key, {"min": m.value, "max": m.value})
          weeks[key]["min"] = min(weeks[key]["min"], m.value)
          weeks[key]["max"] = max(weeks[key]["max"], m.value)
        # 4) Compute “this week is Week 1” labels
        today = date.today()
        cy, cw, _ = today.isocalendar()
        current_monday = date.fromisocalendar(cy, cw, 1)

        injured_data = []
        for (y, w), data in sorted(weeks.items(), reverse=True):
            # Get that week’s Monday
            week_monday = date.fromisocalendar(y, w, 1)
            # Full weeks between current and that week
            weeks_diff = (current_monday - week_monday).days // 7
            # Make it 1‐based: this week → 1, last → 2, etc.
            week_label = f"Week {weeks_diff + 1}"

            low_pct  = (data["min"] - healthy_min) / total_span * 100
            high_pct = (data["max"] - healthy_min) / total_span * 100
            right_pct = 100 - high_pct
            span_pct  = high_pct - low_pct

            injured_data.append({
                "label":    week_label,
                "min":      data["min"],
                "max":      data["max"],
                "low_pct":  low_pct,
                "high_pct": high_pct,
                "right_pct": right_pct,
                "span_pct":  span_pct,
            })

        ctx.update({
            "healthy_min":   healthy_min,
            "healthy_max":   healthy_max,
            "injured_ranges": injured_data,
        })

        return ctx

def attachment_gallery(request):
    attachments = (
      Attachment.objects
          .filter(
              task__user=request.user,
              metrics__isnull=False  # only attachments with at least one metric
          )
          .distinct()                # in case an attachment has multiple metrics
          .order_by('-uploaded_at')
          .prefetch_related('metrics__archetype')
          )
    for att in attachments:
        rel_path = att.image.name

        dirname, filename = os.path.split(rel_path)
        base, ext    = os.path.splitext(filename)
        # build 'attachments/postmark/IMG_4492_postmark.png'
        processed_rel = os.path.join(dirname, 'postmark', f'{base}_postmark{ext}')

        # full disk path to check existence:
        processed_disk = os.path.join(settings.MEDIA_ROOT, processed_rel)

        if os.path.exists(processed_disk):
            # THIS is the URL the browser needs:
            att.postmark_url = settings.MEDIA_URL + processed_rel
        else:
            # fall back to the original image URL
            att.postmark_url = att.image.url
    return render(request, 'tasks/attachment_gallery.html', {'attachments': attachments})