import time
import glob
from face_recognition import load_image_file, face_encodings
from customLogging.customLogging import get_logger
import os

count = 0

# For reading
FAMILIAR_FACES_PATH = '/usr/local/squirrel-ai-mini/data/familiar-faces/'
WANTED_CRIMINALS_PATH = '/usr/local/squirrel-ai-mini/data/wanted-criminals/'

logger = get_logger("ImageLoadService")


def load_criminal_images():
    start_date_time = time.time()
    criminal_cache = [
        next(iter(face_encodings(load_image_file(entry.path))))
        for entry in os.scandir(WANTED_CRIMINALS_PATH) if entry.is_file()
    ]
    # Once the loading is done then print
    logger.info(f"Loaded criminal {len(criminal_cache)} images in {time.time() - start_date_time} seconds")
    return criminal_cache


def load_known_images():
    start_date_time = time.time()
    known_person_cache = []
    for index, path in enumerate(glob.glob(FAMILIAR_FACES_PATH)):
        known_person_image = load_image_file(path)
        try:
            known_person_image_encodings = face_encodings(known_person_image)
            known_person_cache.extend(known_person_image_encodings)
        except IndexError as e:
            logger.error("An exception occurred while reading {0}".format(path))

    # Once the loading is done then print
    logger.info(f"Loaded known {len(known_person_cache)} images in {time.time() - start_date_time} seconds")
    return known_person_cache
