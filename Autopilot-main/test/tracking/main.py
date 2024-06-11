import time
from ultralytics import YOLO
import cv2
from Tracker import TrackObject

CONFIDENCE_THRESHOLD = 0.2
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# initialize the video capture object
video_path = "demo/demo_6.mp4"
video_cap = cv2.VideoCapture(video_path)

# load the pre-trained YOLOv8n model

trackers=[]
last_update = 0
last_model_update= 0
# model = YOLO("yolov8n.pt"
model = YOLO('models/best_2.pt')
while True:
    start = time.time()

    ret, frame = video_cap.read()

    if not ret:
        break

    # up_width = 600
    # up_height = 400
    # up_points = (up_width, up_height)
    # frame = cv2.resize(frame, up_points, interpolation=cv2.INTER_LINEAR)

    ######################################
    # Tracking
    ######################################
    # loop over the detections
    if (start - last_update) > 0.1:
        last_update = start
        for tracker in trackers:
            if tracker.update(frame):
                tracker.show(cv2, frame)
            else:
                trackers.remove(tracker)
        # run the YOLO model on the frame
        if (start - last_model_update) > 1:
            detections = model(frame)[0]
            last_model_update=start
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
                for tr in trackers:
                    if tr.is_same_object(BB):
                        found = True
                        break
                if not found:
                    tracker = TrackObject(frame, BB)
                    trackers.append(tracker)



        # end time to compute the fps
        end = time.time()
        total = (end - start)
        # show the time it took to process 1 frame
        # print(f"Time to process 1 frame: {(end - start).total_seconds() * 1000:.0f} milliseconds")
        # calculate the frame per second and draw it on the frame
        fps = f"FPS: {1 / total:.2f}"
        cv2.putText(frame, fps, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# show the frame to our screen
        cv2.imshow("Frame", frame)

    # writer.write(frame)
    key = cv2.waitKey(20) & 0xFF
    if key == ord(" "):
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):
                break

video_cap.release()

cv2.destroyAllWindows()
