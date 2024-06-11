import cv2 as cv
import numpy as np


class TrackObject(object):
    # constructor function
    def __init__(self, frame, object):
        # self.tracker = cv.TrackerCSRT_create()  # Initialize tracker with CSRT algorithm
        self.tracker = cv.TrackerKCF_create()
        self.tracker.init(frame, object)
        self.BB=object
        # self.id=id


    # https://pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
    def calculate_iou(self,boxA, boxB):

        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2]+boxA[0], boxB[2]+boxB[0])
        yB = min(boxA[3]+boxA[1], boxB[3]+boxB[1])

        # compute the area of intersection rectangle
        interArea =max((xB - xA, 0)) * max((yB - yA), 0)
        if interArea == 0:
            return 0
        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        return iou


    def update(self, frame):
        track_success, self.BB = self.tracker.update(frame)
        return track_success


    def is_same_object(self,  new_object):
        iou=self.calculate_iou(self.BB, new_object)
        # r = iou /(new_object[2]*new_object[3])
        return iou > 0.5

    def show(self,cv, frame):
        BB = self.BB
        top_left = (int(BB[0]), int(BB[1]))
        bottom_right = (int(BB[0] + BB[2]), int(BB[1] + BB[3]))
        cv.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
