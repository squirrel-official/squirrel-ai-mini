import cv2
# This is to pull the information about what each object is called
classNames = []
classFile = "/usr/local/squirrel-ai-mini/model/coco/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# This is to pull the information about what each object should look like
configPath = "/usr/local/squirrel-ai-mini/model/coco/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/usr/local/squirrel-ai-mini/model/coco/frozen_inference_graph.pb"

# This is some set up values to get good results
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


# This is to set up what the drawn box size/colour is and the font/size/colour of the name tag and confidence label
def any_object_found(img, threshold, nms, draw=True, objects=['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'knife']):
    classIds, confs, bbox = net.detect(img, confThreshold=threshold, nmsThreshold=nms)
    object_found = 0
    if len(objects) == 0: objects = classNames
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                object_found = 1
                objectInfo.append([box, className])
                if (draw):
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    return bool(object_found)