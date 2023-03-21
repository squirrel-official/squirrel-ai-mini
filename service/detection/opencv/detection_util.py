import logging

import cv2


def is_human_present(hog, image):
    bounding_box_coordinates, weights = hog.detectMultiScale(image, winStride=(4, 4), padding=(4, 4), scale=1.05)
    person = 0
    for x, y, w, h in bounding_box_coordinates:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, f'person {person}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        person += 1

    if person > 0:
        logging.debug("Human identification passed")
        return True
    else:
        return False


def is_car_present(image):
    car_cascade = cv2.CascadeClassifier("../cascades/cars.xml")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect cars
    cars = car_cascade.detectMultiScale(gray, 1.1, 1)

    no_of_cars = 0
    # Draw border
    for (x, y, w, h) in cars:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        no_of_cars += 1

    if no_of_cars > 0:
        logging.debug("Car identification passed")
        return True
    else:
        return False