import numpy as np
import cv2 as cv


def center(box):
    x = box[0] + int(box[2] / 2)
    y = box[1] + int(box[3] / 2)
    return np.array([np.float32(x), np.float32(y)], np.float32)

class KalmanFilter(object):
    # constructor function
    def __init__(self):
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

        measurement = np.array((2, 1), np.float32)
        prediction = np.zeros((2, 1), np.float32)
        self.kf=kalman

    def predict(self,box):
        # use to correct kalman filter
        self.kf.correct(center(box))

        # get new kalman filter prediction
        prediction = self.kf.predict()

        return prediction