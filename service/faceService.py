import time
from customLogging.customLogging import get_logger
import cv2
import face_recognition
import requests

logger = get_logger("FaceComparisonUtil")
MOTION_VIDEO_URL = '/var/lib/motion/*'
CONFIG_PROPERTIES = '/usr/local/squirrel-ai-mini/config.properties'
ARCHIVE_URL = "/usr/local/squirrel-ai-mini/data/archives/"

# For writing
UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/unknown-visitors/'
CAPTURED_CRIMINALS_PATH = '/usr/local/squirrel-ai-mini/result/captured-criminals/'
KNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/known-visitors/'

# For reading
FAMILIAR_FACES_PATH = '/usr/local/squirrel-ai-mini/data/familiar-faces/*'
WANTED_CRIMINALS_PATH = '/usr/local/squirrel-ai-mini/data/wanted-criminals/*'

CRIMINAL_NOTIFICATION_URL = 'http://my-security.local:8087/criminal'
VISITOR_NOTIFICATION_URL = 'http://my-security.local:8087/visitor'
FRIEND_NOTIFICATION_URL = 'http://my-security.local:8087/friend'


async def analyze_face(image, count_index, criminal_cache, known_person_cache):
    unknown_face_image = extract_face(image)
    if unknown_face_image is not None:
        logger.debug('A new person identified by face so processing it')
        unknown_face_encodings = extract_unknown_face_encodings(unknown_face_image)
        start_date_time = time.time()
        for i, known_encoding in enumerate(criminal_cache + known_person_cache):
            if compare_faces_with_encodings(known_encoding, unknown_face_encodings):
                if i < len(criminal_cache):
                    output_path = CAPTURED_CRIMINALS_PATH
                    url = CRIMINAL_NOTIFICATION_URL
                else:
                    output_path = KNOWN_VISITORS_PATH
                    url = FRIEND_NOTIFICATION_URL
                cv2.imwrite(f"{output_path}frame{count_index}.jpg", unknown_face_image)
                requests.post(url)
                break
        logger.debug("Total comparison time is {0} seconds".format((time.time() - start_date_time)))
        count_index += 1


def extract_face(image):
    face_locations = face_recognition.face_locations(image)
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        return face_image


def extract_unknown_face_encodings(unknown_image):
    unknown_face_locations = face_recognition.face_locations(unknown_image)
    unknown_face_encoding_list = []
    for face_location in unknown_face_locations:
        top, right, bottom, left = face_location
        unknown_face_image = unknown_image[top:bottom, left:right]
        for each_unknown_face_encoding in face_recognition.face_encodings(unknown_face_image):
            unknown_face_encoding_list.append(each_unknown_face_encoding)
    # Returning unknown face encodings
    return unknown_face_encoding_list


def compare_faces_with_encodings(known_image_encoding, unknown_image_encoding_list, each_wanted_criminal_path):
    for each_unknown_face_encoding in unknown_image_encoding_list:
        face_compare_list = face_recognition.compare_faces([each_unknown_face_encoding], known_image_encoding, 0.5)
        # show the image if it  has matched
        for face_compare in face_compare_list:
            if face_compare:
                print("face comparison match with %s" % each_wanted_criminal_path)
                return True


