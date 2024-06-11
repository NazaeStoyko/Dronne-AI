from ultralytics import YOLO
from Tracking.Tracker import TrackObject
CONFIDENCE_THRESHOLD = 0.5

class ObjectDetection(object):
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def update(self, frame, trackers ):
        detections = self.model(frame, classes=0)[0]
        for data in detections.boxes.data.tolist():
            # extract the confidence (i.e., probability) associated with the prediction
            confidence = data[4]
            # filter out weak detections by ensuring the
            # confidence is greater than the minimum confidence
            if float(confidence) < CONFIDENCE_THRESHOLD:
                continue

            # if the confidence is greater than the minimum confidence,
            # get the bounding box and the class id
            xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            class_id = int(data[5])
            # add the bounding box (x, y, w, h), confidence and class id to the results list
            # results.append([[xmin, ymin, xmax - xmin, ymax - ymin], confidence, class_id])
            print('confidence - ', data)
            box = list((xmin, ymin, xmax - xmin, ymax - ymin))
            BB = tuple(box)

            #  Update list of tracking
            found = False
            for item in trackers:
                if item.is_same_object(BB):
                    found = True
                    break
            if not found:
                tracker = TrackObject(frame, BB)
                trackers.append(tracker)

        return trackers