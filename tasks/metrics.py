from .models import Attachment, Metric, MetricArchetype, PoseLandmarkType
from .utils import calculate_angle_3d, calculate_angle_2d
import logging
from typing import Dict, Any
from django.db import transaction


logger = logging.getLogger(__name__)

def compute_knee_angles(att,detection_result):
    archetypes = MetricArchetype.objects.filter(name="knee_angle").reverse()
    world_landmarks = detection_result.pose_world_landmarks[0]
    normalised_landmarks = detection_result.pose_landmarks[0]
    with transaction.atomic():
      for archetype in archetypes:
        print(f"Computing {archetype.slug} for attachment {att.image.name}")
        world_p1, world_p2, world_p3 = (world_landmarks[i] for i in archetype.landmark_indexes)
        normalised_p1, normalised_p2, normalised_p3 = (normalised_landmarks[i] for i in archetype.landmark_indexes)
        accuracy = min([world_p1.visibility, world_p2.visibility, world_p3.visibility])
        if accuracy < 0.3:
          logger.warning(f"Low visibility for knee angle landmarks in {archetype.slug} for attachment {att.image.name}")
        else:
          world_metric = calculate_angle_3d(world_p1, world_p2, world_p3)
          normalised_metric = calculate_angle_2d(normalised_p1, normalised_p2, normalised_p3)
          if normalised_metric <20:
            value = normalised_metric
          else:
            value = world_metric
          Metric.objects.update_or_create(
              attachment=att,
              archetype=archetype,
              defaults={'value': value, 'accuracy': accuracy}
          )





