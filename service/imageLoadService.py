import time
import glob
from face_recognition import load_image_file, face_encodings
from customLogging.customLogging import get_logger

count = 0

# For reading
FAMILIAR_FACES_PATH = '/usr/local/squirrel-ai-mini/data/familiar-faces/*'
WANTED_CRIMINALS_PATH = '/usr/local/squirrel-ai-mini/data/wanted-criminals/*'

logger = get_logger("ImageLoadService")


def load_criminal_images():
    criminal_cache = []
    start_date_time = time.time()
    for eachWantedCriminalPath in glob.glob(WANTED_CRIMINALS_PATH):
        criminal_image = load_image_file(eachWantedCriminalPath)
        try:
            criminal_image_encoding = face_encodings(criminal_image)[0]
            criminal_cache.append(criminal_image_encoding)
        except IndexError as e:
            logger.error("An exception occurred while reading {0}".format(eachWantedCriminalPath))
    # Once the loading is done then print
    logger.info(
        "Loaded criminal  {0} images in {1} seconds".format(len(criminal_cache), (time.time() - start_date_time)))
    return criminal_cache


def load_known_images():
    known_person_cache = []
    start_date_time = time.time()
    for eachWantedKnownPersonPath in glob.glob(FAMILIAR_FACES_PATH):
        known_person_image = load_image_file(eachWantedKnownPersonPath)
        try:
            known_person_image_encoding = face_encodings(known_person_image)[0]
            known_person_cache.append(known_person_image_encoding)
        except IndexError as e:
            logger.error("An exception occurred while reading {0}".format(eachWantedKnownPersonPath))
    # Once the loading is done then print
    logger.info(
        "Loaded known  {0} images in {1} seconds".format(len(known_person_cache), (time.time() - start_date_time)))
    return known_person_cache