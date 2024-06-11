import numpy as np
import cv2 as cv
from Tracking.Helper import get_center


# Prediction object
class Prediction(object):
    # constructor function
    def __init__(self):
        # use  Kaman filter for building prediction
        kalman = cv.KalmanFilter(4, 2)
        kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                             [0, 1, 0, 0]], np.float32)

        kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                            [0, 1, 0, 1],
                                            [0, 0, 1, 0],
                                            [0, 0, 0, 1]], np.float32)

        kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]], np.float32) * 0.03

        # measurement = np.array((2, 1), np.float32)
        # prediction = np.zeros((2, 1), np.float32)
        self.__kf=kalman

    def update(self,box):
        # use to correct kalman filter
        (x, y, w, h) = [int(v) for v in box]
        self.__kf.correct(get_center(box))

        # get new kalman filter prediction
        prediction= self.__kf.predict()
        # get predicton's center
        px = prediction[0][0]
        py = prediction[1][0]
        b = list(box)
        b[0] = int(px - (0.5 * w))
        b[1] = int(py - (0.5 * h))
        box = tuple(b)
        return box

