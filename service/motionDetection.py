# import the opencv module
import time
import cv2
from customLogging.customLogging import get_logger
# Initializing things
from detection.tensorflow.tf_coco_ssd_algorithm import tensor_coco_ssd_mobilenet
from detection.tensorflow.coco import any_object_found
from faceService import analyze_face
from imageLoadService import load_criminal_images, load_known_images
from emailService import generate_email, send_email

from multiprocessing import Process

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
    try:
        motion_detected = False
        start_frame = None
        frames_saved = 0
        capture = cv2.VideoCapture(streamUrl)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        fps = capture.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter("/usr/local/squirrel-ai-mini/{0}.avi".format(time.time()), fourcc, fps, (FRAME_WIDTH, FRAME_HEIGHT))

        if not capture.isOpened():
            logger.error("Error opening video file {}".format(streamUrl))

        frame_count = 1
        image_count = 1
        object_detection_flag = 0
        if capture.isOpened():
            ret, image = capture.read()
            logger.info(" Processing file {0} ".format(streamUrl))
            while ret:
                if tensor_coco_ssd_mobilenet(image) and any_object_found(image, 0.50, 0.4):
                    logger.debug("Object detected, flag :{0}".format(object_detection_flag))
                    print(fps)
                    if object_detection_flag == 0:
                        object_detection_flag = 1
                    complete_file_name = UNKNOWN_VISITORS_PATH + str(camera_id) + "-" + str(image_count) + '.jpg'
                    image_count = image_count + 1
                    cv2.imwrite(complete_file_name, image)
                    msg = generate_email(from_user, to_user, complete_file_name)
                    send_email(msg, from_user, from_pwd, to_user)
                    analyze_face(image, frame_count, criminal_cache, known_person_cache)

                    if not motion_detected:
                        motion_detected = True
                        start_frame = capture.get(cv2.CAP_PROP_POS_FRAMES) - frames_to_save_before_motion

                # If motion is detected, save the video of the motion
                if motion_detected and frames_saved < frames_to_save_before_motion + frames_to_save_after_motion:
                    if capture.get(cv2.CAP_PROP_POS_FRAMES) >= start_frame:
                        out.write(image)
                        print('saved to frame: {0}'.format(frames_saved))
                        frames_saved += 1
                elif motion_detected:
                    motion_detected = False
                    frames_saved = 0
                    out.release()

                ret, image = capture.read()
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


def start_monitoring():
    try:
        criminal_cache = load_criminal_images()
        known_person_cache = load_known_images()
        # monitor_camera_stream(GARAGE_EXTERNAL_CAMERA_STREAM, 1, criminal_cache, known_person_cache)
        p1 = Process(target=monitor_camera_stream,
                     args=(GARAGE_EXTERNAL_CAMERA_STREAM, 1, criminal_cache, known_person_cache,))
        p1.start()
        p1.join()
    except Exception as e:
        logger.error("An exception occurred.")
        logger.error(e, exc_info=True)


start_monitoring()
