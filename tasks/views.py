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

from django.db.models import Min, Max

class KneeMobilityView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/knee_mobility.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        left_arc  = MetricArchetype.objects.get(slug="left_knee_angle")
        right_arc = MetricArchetype.objects.get(slug="right_knee_angle")

        left_vals = Metric.objects.filter(archetype=left_arc)
        # aggregate() returns e.g. {'value__min': 10.0}
        ctx['left_min'] = left_vals.aggregate(min_val=Min('value'))['min_val'] or 0.0
        ctx['left_max'] = left_vals.aggregate(max_val=Max('value'))['max_val'] or 135.0

        right_vals = Metric.objects.filter(archetype=right_arc)
        ctx['right_min'] = right_vals.aggregate(min_val=Min('value'))['min_val'] or ctx['left_min']
        ctx['right_max'] = right_vals.aggregate(max_val=Max('value'))['max_val'] or ctx['left_max']

        injured = (
            Metric.objects
                  .filter(archetype=right_arc)
                  .order_by('-computed_at')
                  .first()
        )
        ctx['current'] = injured.value if injured else ctx['right_min']

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