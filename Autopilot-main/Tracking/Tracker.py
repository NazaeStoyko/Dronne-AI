import cv2 as cv
from Tracking.Helper import calculate_iou
from Tracking.Prediction import Prediction


class TrackObject(object):
    # constructor function
    def __init__(self, frame, object, type='KCF', use_prediction= False):
        #  Initialize tracker
        if type == 'KCF':
            self.__tracker = cv.TrackerKCF_create()
        if type == 'SCRT':
            self.__tracker = cv.TrackerCSRT_create()

        self.__tracker.init(frame, object)
        self.__BB = object


        self.__color = (255, 0, 0)  # blue
        self.__color_predict = (0,255,) # green
        self.__use_prediction=use_prediction
        self.__predict=None
        if self.__use_prediction:
            self.__predict = Prediction()
            self.__predict_BB = object
            # train prediction
            for i in range(100):
                self.__predict.update(self.__BB)
        # self.id=id


    def update(self, frame):
        # update tracking object
        track_success, self.__BB = self.__tracker.update(frame)
        if track_success:
            if self.__use_prediction:
                self.__predict_BB = self.__predict.update(self.__BB)

        return track_success


    def is_same_object(self,  new_object):
        # calc the boxes  intersection area
        iou = calculate_iou(self,self.__BB, new_object)
        return iou > 0.5

    def get_target(self):
        # calc the boxes  intersection area
        if self.__use_prediction:
            return self.__predict_BB
        else:
            return self.__BB


    def show(self,cv, frame, _color=None):
        # show rectangle in opencv frame
        (x, y, w, h) = [int(v) for v in self.__BB]
        color = _color
        if not color:
            color = self.__color
        cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        if self.__use_prediction:
            (x, y, w, h) = [int(v) for v in self.__predict_BB]
            cv.rectangle(frame, (x, y), (x + w, y + h), self.__color_predict, 2)

