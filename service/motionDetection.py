# import the opencv module
import time
import cv2
from customLogging.customLogging import get_logger
# Initializing things
from detection.tensorflow.tf_coco_ssd_algorithm import tensor_coco_ssd_mobilenet
from detection.tensorflow.coco import any_object_found
from faceService import analyze_face
from imageLoadService import load_criminal_images, load_known_images
import requests
from multiprocessing import Process

# For writing
UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/unknown-visitors/'

GARAGE_EXTERNAL_CAMERA_STREAM = '/dev/video0'
NOTIFICATION_URL = 'http://my-security.local:8087/visitor'
count = 0
ssd_model_path = '/usr/local/squirrel-ai-mini/model/coco-ssd-mobilenet'
efficientdet_lite0_path = '/usr/local/squirrel-ai-mini/model/efficientdet-lite0/efficientdet_lite0.tflite'
logger = get_logger("Motion Detection")


def monitor_camera_stream(streamUrl, camera_id, criminal_cache, known_person_cache):
    try:
        capture = cv2.VideoCapture(streamUrl)
        if not capture.isOpened():
            logger.error("Error opening video file {}".format(streamUrl))

        frame_count = 1
        image_count = 1
        object_detection_flag = 0
        detection_counter = time.time()
        if capture.isOpened():
            ret, image = capture.read()
            logger.info(" Processing file {0} ".format(streamUrl))
            while ret:
                if tensor_coco_ssd_mobilenet(image) and any_object_found(image, 0.50, 0.4):
                    logger.debug("Object detected, flag :{0}".format(object_detection_flag))
                    if object_detection_flag == 0:
                        detection_counter = time.time()
                        object_detection_flag = 1
                    complete_file_name = UNKNOWN_VISITORS_PATH + str(camera_id) + "-" + str(image_count) + '.jpg'
                    image_count = image_count + 1
                    cv2.imwrite(complete_file_name, image)
                    analyze_face(image, frame_count, criminal_cache, known_person_cache)

                if (time.time() - detection_counter) > 3 and object_detection_flag == 1:
                    object_detection_flag = 0
                    data = requests.post(NOTIFICATION_URL)
                    logger.info("Detected activity sent notification, response : {0}".format(data))
                ret, image = capture.read()
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


def start_monitoring():
    try:
        criminal_cache = load_criminal_images()
        known_person_cache = load_known_images()
        # monitor_camera_stream(GARAGE_EXTERNAL_CAMERA_STREAM, 1, criminal_cache, known_person_cache)
        p1 = Process(target=monitor_camera_stream, args=(GARAGE_EXTERNAL_CAMERA_STREAM, 1, criminal_cache, known_person_cache,))
        p1.start()
        p1.join()
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


start_monitoring()