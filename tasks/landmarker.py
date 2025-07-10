import os, sys
import io
from PIL import Image
import cv2
import mediapipe as mp
from mediapipe import solutions
from django.conf import settings
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, pose
from mediapipe.python.solutions.drawing_styles import get_default_pose_landmarks_style


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def analyse_pose_landmark(attachment):
  # Get the local filesystem path
  file_path = attachment.image.path
  # Configure the landmarker
  base_options = python.BaseOptions(model_asset_path=str(settings.POSE_LANDMARKER_MODEL_PATH))
  options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionRunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
    )
  # Run the inference
  detector = vision.PoseLandmarker.create_from_options(options)
  image = mp.Image.create_from_file(file_path)
  detection_result = detector.detect(image)
  return detection_result

def draw_landmarks_on_image(attachment,detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    pil_img = Image.open(attachment.image.path).convert("RGB")
    annotated_image = np.array(pil_img)

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
      pose_landmarks = pose_landmarks_list[idx]

      # Draw the pose landmarks.
      pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
      pose_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
      ])
      solutions.drawing_utils.draw_landmarks(
        annotated_image,
        pose_landmarks_proto,
        solutions.pose.POSE_CONNECTIONS,
        solutions.drawing_styles.get_default_pose_landmarks_style())

    return annotated_image

def save_landmarks_image(attachment, detection_result):
  base, ext = os.path.splitext(attachment.image.name)
  fname = f"{base}_postmark{ext}"
  print(fname)         # "attachments/IMG_1234_postmark.jpg"
  storage_path = os.path.join(
      os.path.dirname(fname),
      "postmark",
      os.path.basename(fname)
  )
  print(storage_path)  # "attachments/postmark/IMG_1234_postmark.jpg"
  annotated_image = draw_landmarks_on_image(attachment, detection_result)
  # annotated_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

  buf = io.BytesIO()
  Image.fromarray(annotated_image).save(buf, format=ext.lstrip(".").upper())
  buf.seek(0)
  saved_path = default_storage.save(storage_path, ContentFile(buf.read()))
  return saved_path
#   base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
# options = vision.PoseLandmarkerOptions(
#     base_options=base_options,
#     output_segmentation_masks=True)
# detector = vision.PoseLandmarker.create_from_options(options)

# # STEP 3: Load the input image.
# image = mp.Image.create_from_file("IMG_4472 (1).jpeg")

# # STEP 4: Detect pose landmarks from the input image.
# detection_result = detector.detect(image)

# # STEP 5: Process the detection result. In this case, visualize it.
# annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
# cv2_imshow(cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))



# options = PoseLandmarkerOptions(
#     base_options=BaseOptions(model_asset_path=model_path),
#     running_mode=VisionRunningMode.IMAGE)

# with PoseLandmarker.create_from_options(options) as landmarker:
#   # The landmarker is initialized. Use it here.