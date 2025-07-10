from .models import Attachment, Metric, MetricArchetype, PoseLandmarkType
from .utils import calculate_angle
import logging
from typing import Dict, Any
from django.db import transaction


logger = logging.getLogger(__name__)

def compute_knee_angles(att):
    landmarks = {
        lm.location_index.location_index: lm
        for lm in att.landmarks.all()
    }
    archetypes = MetricArchetype.objects.filter(name="knee_angle")

    with transaction.atomic():
      for archetype in archetypes:
          print(archetype.slug, archetype.landmark_indexes)
          idx1, idx2, idx3 = archetype.landmark_indexes
          missing = [i for i in (idx1, idx2, idx3) if i not in landmarks]
          if missing:
              logger.warning(
                  f"Missing landmarks {missing} for archetype {archetype.name} in attachment {att.image.path}"
              )
              continue


          p1, p2, p3 = (landmarks[i] for i in (idx1, idx2, idx3))
          print(p1, p2, p3)
          val = calculate_angle(
                (p1.x, p1.y, p1.z),
                (p2.x, p2.y, p2.z),
                (p3.x, p3.y, p3.z),
            )
          accuracy = (p1.visibility + p2.visibility + p3.visibility)/3.0

          Metric.objects.update_or_create(
              attachment=att,
              archetype=archetype,
              defaults={'value': val, 'accuracy': accuracy}
          )
          logger.info(f"Computed knee angles for {archetype.name} with {val} for attachment {att.image.name}")





