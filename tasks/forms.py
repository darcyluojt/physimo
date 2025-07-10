from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils import timezone
from .models import Task, Category

class TaskForm(forms.ModelForm):
  attachment = forms.FileField(
        required=False,
        widget=ClearableFileInput,  # shows existing file and allows clearing
        help_text="Upload one photo."
    )

  class Meta:
    model = Task
    fields = ['category', 'title', 'notes', 'attachment', 'start_time', 'end_time', 'done']
    widgets = {
      'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
      'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    }

  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # Set default start time to now
        if not self.instance.pk:  # Only set if creating a new instance
          self.fields['start_time'].initial = timezone.now()

