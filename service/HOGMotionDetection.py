import cv2

UNKNOWN_VISITORS_PATH = '/usr/local/squirrel-ai-mini/result/unknown-visitors/'


def monitor_camera_stream():
    # Load the pre-trained HOG (Histogram of Oriented Gradients) model for pedestrian detection
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Open the camera
    cap = cv2.VideoCapture(0)  # Change the parameter to the appropriate camera index if necessary
    image_count = 1
    frame_count = 1
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        if not ret:
            break

        # Resize the frame to improve processing speed
        frame = cv2.resize(frame, (640, 480))

        # Perform pedestrian detection
        boxes, weights = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)

        # Draw bounding boxes around detected pedestrians
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the resulting frame
            complete_file_name = f"{UNKNOWN_VISITORS_PATH}-{image_count}.jpg"
            image_count += 1
            cv2.imwrite(complete_file_name, frame)
            # cv2.imshow('Pedestrian Detection', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera and close any open windows
    cap.release()
    cv2.destroyAllWindows()


monitor_camera_stream()
