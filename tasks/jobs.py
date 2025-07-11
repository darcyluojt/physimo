import logging
from .landmarker import analyse_pose_landmark
from .models import Attachment, PoseLandmark, PoseLandmarkType, Task
from .landmarker import analyse_pose_landmark, save_landmarks_image
from .metrics import compute_knee_angles

logger = logging.getLogger(__name__)

def attachment_processing(attachment):
    detection_result = analyse_pose_landmark(attachment)
    if not detection_result.pose_world_landmarks:
        logger.warning(f"No pose world landmarks found for attachment {attachment.pk}.")
        return

    save_landmarks_image(attachment, detection_result)

    compute_knee_angles(attachment, detection_result)

