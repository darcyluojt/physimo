import logging
from .landmarker import analyse_pose_landmark
from .models import Attachment, PoseLandmark, PoseLandmarkType, Task
from .landmarker import analyse_pose_landmark, save_landmarks_image
from .metrics import compute_knee_angles

logger = logging.getLogger(__name__)

def attachment_processing(attachment):
    detection_result = analyse_pose_landmark(attachment)
    data = detection_result.pose_world_landmarks
    if not data:
        logger.warning(f"No pose landmarks found for attachment {attachment.pk}.")
        return
    if attachment.landmarks.exists():
        logger.info(f"Pose landmarks already exist for attachment {attachment.pk}. Skipping processing.")
    else:
        result = data[0]
        logger.info(f"Processing pose landmarks for attachment {attachment.pk} {attachment.image.name}.")
    # Prepare only those with index ≥ 11
        to_save = []
        for idx, lm in enumerate(result):
            if idx <= 10:
                continue
            elif lm.visibility > 0.1:
                to_save.append(PoseLandmark(
                    attachment      = attachment,
                    location_index  = PoseLandmarkType.objects.get(location_index=idx),
                    x                = lm.x,
                    y                = lm.y,
                    z                = lm.z,
                    visibility       = getattr(lm, "visibility", None),
                    presence        = getattr(lm, "presence", None),
                    captured_at      = attachment.task.start_time,  # Use the attachment's upload time
                ))
                PoseLandmark.objects.bulk_create(to_save, ignore_conflicts=True)
    # Call the job to compute the angles
    logger.info(f"Saving annotated image for attachment {attachment.pk}.")
    save_landmarks_image(attachment, detection_result)
    compute_knee_angles(attachment)

