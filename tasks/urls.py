# tasks/urls.py

from django.urls import path
from .views import TaskCreateView, TodayTasksListView   # you’ll fill in views as you build them

app_name = "tasks"

urlpatterns = [
  path("new/", TaskCreateView.as_view(), name="task-create"),
  path("today/", TodayTasksListView.as_view(), name="task-list-today"),
    # e.g. path("", views.TaskListView.as_view(), name="task-list"),
]
#