from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    colour_code = models.CharField(max_length=7, default='#FFFFFF')  # Default to white

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Task(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True
    )
    category    = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True
    )
    title       = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Optional title; can be empty as long as category is set.'
    )
    notes       = models.TextField(blank=True, null=True)
    start_time  = models.DateTimeField(default=timezone.now)
    end_time    = models.DateTimeField(null=True, blank=True)
    done        = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Task #{self.pk}"
# Create your models here.
class Attachment(models.Model):
    task        = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='attachment',
        db_index=True)
    image       = models.ImageField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}: {self.image.name}"

class PoseLandmark(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name='landmarks',
        db_index=True
    )
    location_index = models.ForeignKey(
        'PoseLandmarkType',
        on_delete=models.CASCADE,
        db_index=True
    )
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)
    visibility = models.FloatField(blank=True, null=True)
    presence = models.FloatField(blank=True, null=True)
    captured_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attachment', 'location_index')
        indexes = [
            models.Index(fields=['attachment', 'location_index']),
        ]

    def __str__(self):
        return f"Landmark {self.location_index} for Attachment {self.attachment_id} with visbility {self.visibility}"

class PoseLandmarkType(models.Model):
    location_index = models.PositiveIntegerField(
        unique=True)
    name = models.CharField(
        max_length=100)

    def __str__(self):
        return f"Landmark {self.location_index}: {self.name}"

class MetricArchetype(models.Model):
    """
    Defines *what* we measure and *how* to interpret it.
    E.g. "knee_angle", side="left" or "right", description, maybe a slug for your code.
    """
    name             = models.CharField(
        max_length=100,
        help_text="E.g. 'knee_angle'"
    )
    side             = models.CharField(
        max_length=6,
        choices=[("left","Left"),("right","Right"),("center","Center")],
        help_text="Which side of the body this metric applies to"
    )
    slug             = models.SlugField(
        unique=True,
        help_text="Machine-friendly identifier, e.g. 'left_knee_angle'"
    )
    description      = models.TextField(
        blank=True,
        help_text="Optional human-readable description"
    )
    landmark_indexes = models.JSONField(
        default=list,
        help_text=(
            "List of MediaPipe landmark indexes used in this calculation, "
            "e.g. [23,25,27] for hip→knee→ankle"
        )
    )
    @property
    def title(self):
        # replace underscores with spaces, then Title Case
        return self.slug.replace('_', ' ').title()

    def __str__(self):
        return f"{self.get_side_display()} {self.name.replace('_',' ').title()}: {self.landmark_indexes}"


class Metric(models.Model):
    """
    Stores one computed value for one attachment & archetype.
    """
    attachment      = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="metrics"
    )
    archetype       = models.ForeignKey(
        MetricArchetype,
        on_delete=models.CASCADE,
        related_name="metrics"
    )
    value           = models.FloatField()
    computed_at     = models.DateTimeField(auto_now_add=True)
    accuracy        = models.FloatField()


    class Meta:
        unique_together = [["attachment","archetype"]]
        indexes = [models.Index(fields=["archetype","computed_at"])]

    def __str__(self):
        return f"{self.archetype}={self.value:.1f} at {self.computed_at:%Y-%m-%d %H:%M}"
