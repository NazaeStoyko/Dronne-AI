import time
import math
from Tracking.Helper import get_center


class TargetObject(object):
    def __init__(self, box, color,use_target=False):
        self.__box = box
        self.__color = color
        self.__use_target=use_target

    def get_center(self):
        return get_center(self.__box)

    def get_target(self):
        return self.__box

    def show(self, cv, frame):
        color=self.__color
        (x, y, w, h) = [int(v) for v in self.__box]

        cv.rectangle(frame, (x , y), (x+w, y+h), color, 2)
        if self.__use_target:
            cv.line(frame, (x + int(w/2), y), (x + int(w/2), y+ h), color, 1)
            cv.line(frame, (x, y + int(h/2)), (x + w, y + int(h/2)), color, 1)


