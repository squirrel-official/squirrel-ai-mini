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
from contextlib import contextmanager

UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/unknown-visitors/'
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


def monitor_camera_stream(criminal_cache, known_person_cache):
    motion_detected = False
    frames_saved = 0
    logger.debug(cv2.VideoCapture('/dev/video0'))
    with (cv2.VideoCapture('/dev/video0')) as capture:
        if not capture.isOpened():
            logger.error(f"Error opening video file {'/dev/video0'}")

        image_count = 1
        frame_count = 1
        object_detection_flag = 0
        if capture.isOpened():
            ret, image = capture.read()
            while ret:
                if tensor_coco_ssd_mobilenet(image) and any_object_found(image, 0.50, 0.4):
                    logger.debug("detection")
                    if object_detection_flag == 0:
                        object_detection_flag = 1
                    complete_file_name = f"{UNKNOWN_VISITORS_PATH}-{image_count}.jpg"
                    image_count += 1
                    cv2.imwrite(complete_file_name, image)
                    message = generate_email(from_user, to_user, complete_file_name)
                    send_email_and_face_compare(message, image, frame_count, criminal_cache, known_person_cache)

                ret, image = capture.read()
                frame_count = frame_count + 1


def send_email_and_face_compare(message, image, frame_count, criminal_cache, known_person_cache):
    try:

        send_email(message, from_user, from_pwd, to_user)
        analyze_face(image, frame_count, criminal_cache, known_person_cache)

    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


def start_monitoring():
    try:
        criminal_cache = load_criminal_images()
        known_person_cache = load_known_images()
        monitor_camera_stream(criminal_cache, known_person_cache)
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


start_monitoring()
