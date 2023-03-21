import time

from customLogging.customLogging import get_logger
from PIL import Image
import cv2
import face_recognition
from face_recognition import load_image_file, face_encodings
import requests

logger = get_logger("FaceComparisonUtil")
MOTION_VIDEO_URL = '/var/lib/motion/*'
CONFIG_PROPERTIES = '/usr/local/squirrel-ai/config.properties'
ARCHIVE_URL = "/usr/local/squirrel-ai/data/archives/"

# For writing
UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai/result/unknown-visitors/'
CAPTURED_CRIMINALS_PATH = '/usr/local/squirrel-ai/result/captured-criminals/'
KNOWN_VISITORS_PATH = '/usr/local/squirrel-ai/result/known-visitors/'

# For reading
FAMILIAR_FACES_PATH = '/usr/local/squirrel-ai/data/familiar-faces/*'
WANTED_CRIMINALS_PATH = '/usr/local/squirrel-ai/data/wanted-criminals/*'

CRIMINAL_NOTIFICATION_URL = 'http://my-security.local:8087/criminal'
VISITOR_NOTIFICATION_URL = 'http://my-security.local:8087/visitor'
FRIEND_NOTIFICATION_URL = 'http://my-security.local:8087/friend'


def analyze_face(image, count_index, criminal_cache, known_person_cache):
    unknown_face_image = extract_face(image)
    if unknown_face_image is not None:
        logger.debug('A new person identified by face so processing it')
        unknown_face_image_encodings = extract_unknown_face_encodings(unknown_face_image)
        # saving the image to visitor folder
        start_date_time = time.time()
        for each_criminal_encoding in criminal_cache:
            if compare_faces_with_encodings(each_criminal_encoding, unknown_face_image_encodings,
                                            "eachWantedCriminalPath"):
                cv2.imwrite('{}criminal-frame{:d}.jpg'.format(CAPTURED_CRIMINALS_PATH, count_index),
                            unknown_face_image)
                requests.post(CRIMINAL_NOTIFICATION_URL)

        for each_known_encoding in known_person_cache:
            if compare_faces_with_encodings(each_known_encoding, unknown_face_image_encodings,
                                            "eachWantedKnownPath"):
                cv2.imwrite('{}known-frame{:d}.jpg'.format(KNOWN_VISITORS_PATH, count_index),
                            unknown_face_image)
                requests.post(FRIEND_NOTIFICATION_URL)
        logger.debug("Total comparison time is {0} seconds".format((time.time() - start_date_time)))
        count_index += 1


def extract_face(image):
    face_locations = face_recognition.face_locations(image)
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
        #                                                                                             right))
        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        # pil_image = Image.fromarray(face_image)
        return face_image


def compare_faces(known_image_encoding, unknown_image_encoding, each_wanted_criminal_path):
    unknown_face_locations = face_recognition.face_locations(unknown_image_encoding)

    for face_location in unknown_face_locations:
        top, right, bottom, left = face_location
        unknown_face_image = unknown_image_encoding[top:bottom, left:right]
        for each_unknown_face_encoding in face_recognition.face_encodings(unknown_face_image):
            face_compare_list = face_recognition.compare_faces([each_unknown_face_encoding], known_image_encoding, 0.5)
            # show the image if it  has matched
            for face_compare in face_compare_list:
                if face_compare:
                    print("face comparison match with %s" % each_wanted_criminal_path)
                    return True


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


def compare_faces_with_path(known_image_path, unknown_image_path):
    # known_image = face_recognition.load_image_file("/Users/anil/Desktop/saurabh.jpeg")
    known_image = load_image_file(known_image_path)
    known_image_encoding = face_encodings(known_image)[0]

    # image = face_recognition.load_image_file("/Users/anil/Desktop/test1.png")
    unknown_image = load_image_file(unknown_image_path)
    unknown_face_locations = face_recognition.face_locations(unknown_image)

    for face_location in unknown_face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        logger.debug(
            "A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
                                                                                                  right))

        # You can access the actual face itself like this:
        unknown_face_image = unknown_image[top:bottom, left:right]
        pil_image = Image.fromarray(unknown_face_image)
        unknown_encoding = face_recognition.face_encodings(unknown_face_image)[0]
        face_compare_list = face_recognition.compare_faces([unknown_encoding], known_image_encoding)
        # show the image if it  has matched
        for face_compare in face_compare_list:
            if face_compare:
                # pil_image.show()
                return True