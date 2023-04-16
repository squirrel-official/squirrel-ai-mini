# import the opencv module
import time
import cv2
import asyncio
from customLogging.customLogging import get_logger
import datetime
# Initializing things
from detection.tensorflow.tf_coco_ssd_algorithm import tensor_coco_ssd_mobilenet
from detection.tensorflow.coco import any_object_found
from faceService import analyze_face
from imageLoadService import load_criminal_images, load_known_images
from emailService import generate_email, send_email, send_email_async


UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/unknown-visitors/'
GARAGE_EXTERNAL_CAMERA_STREAM = '/dev/video0'
NOTIFICATION_URL = 'http://my-security.local:8087/visitor'

from_user = "anil.kumar.ait09@gmail.com"
from_pwd = "pw"
to_user = "anil.kumar.ait09@gmail.com"

frames_to_save_before_motion = 15
frames_to_save_after_motion = 15
count = 0
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
ssd_model_path = '/usr/local/squirrel-ai-mini/model/coco-ssd-mobilenet'
efficientdet_lite0_path = '/usr/local/squirrel-ai-mini/model/efficientdet-lite0/efficientdet_lite0.tflite'
logger = get_logger("Motion Detection")


def monitor_camera_stream(streamUrl, camera_id, criminal_cache, known_person_cache):
    motion_detected = False
    frames_saved = 0
    with cv2.VideoCapture(streamUrl) as capture:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        fps = capture.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f"/usr/local/squirrel-ai-mini/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.avi",
                              fourcc, fps, (FRAME_WIDTH, FRAME_HEIGHT))

        if not capture.isOpened():
            logger.error(f"Error opening video file {streamUrl}")

        image_count = 1
        object_detection_flag = 0
        for frame_count, image in enumerate(iter(capture.read, (False, None))):
            if tensor_coco_ssd_mobilenet(image) and any_object_found(image, 0.50, 0.4):
                if object_detection_flag == 0:
                    object_detection_flag = 1
                complete_file_name = f"{UNKNOWN_VISITORS_PATH}{camera_id}-{image_count}.jpg"
                image_count += 1
                cv2.imwrite(complete_file_name, image)
                message = generate_email(from_user, to_user, complete_file_name)
                send_email_and_face_compare(message, image, frame_count, criminal_cache, known_person_cache)

                if not motion_detected:
                    motion_detected = True
                    start_frame = capture.get(cv2.CAP_PROP_POS_FRAMES) - frames_to_save_before_motion

            if motion_detected and frames_saved < frames_to_save_before_motion + frames_to_save_after_motion:
                current_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)
                if current_frame >= start_frame:
                    out.write(image)
                    logger.debug(f"saved to frame: {frames_saved}")
                    frames_saved += 1
            elif motion_detected:
                motion_detected = False
                frames_saved = 0
                out.release()


def send_email_and_face_compare(message, image, frame_count, criminal_cache, known_person_cache):
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_email(message, from_user, from_pwd, to_user))
        loop.run_until_complete(analyze_face(image, frame_count, criminal_cache, known_person_cache))

    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


def start_monitoring():
    try:
        criminal_cache = load_criminal_images()
        known_person_cache = load_known_images()
        monitor_camera_stream(GARAGE_EXTERNAL_CAMERA_STREAM, 1, criminal_cache, known_person_cache)
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


start_monitoring()
