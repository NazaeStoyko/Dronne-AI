import os
import cv2 as cv
from ObjectDetection import ObjectDetection
from Stratagy import ObjectStrategy
from Tracking.Tracker import TrackObject
from Tracking.Target import TargetObject
from BaseObject import Point

import time

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

class ObjectTracking(object):
    # constructor function
    def __init__(self, vehicle,config={}):
        # rotate_mode = True, camera_id = 0, use_prediction = False, fullscreen = True, use_stabilize = False, camera_in_front = True, use_object_detection = False
        self.vehicle = vehicle
        # camera_id='Tracking/2.mp4'
        self.camera_id = config.get('camera_id',0)
        self.tracker = None  # Initialize tracker with CSRT algorithm
        self.target = None  # target Bounding Box
        self.strategy = ObjectStrategy(vehicle, config)
        self.use_prediction = config.get('use_prediction', False)
        self.fullscreen_mode = config.get('fullscreen',True)
        self.target_size = config.get('target_size', 30)  # 30 picsels default
        self.stabilize_size = config.get('stabilize_size',120)  # 120 picsels
        # self.camera_in_front = config.get('camera', True)['in_front']
        self.use_stabilize = config.get('use_stabilize', False)
        self.use_object_detection = config.get('use_object_detection', False)
        self.need_tracking = False
        self.selected_object = None
        if self.use_object_detection:
            self.vehicle.listen_command(self.do_command)
            self.selected_color = (0, 0, 255)  # red
            self.trackers = []

    def init_tracker(self, frame):
        # init  CSRT tracker
        self.tracker = TrackObject(frame, self.target, 'SCRT', self.use_prediction)

    def move_vehicle(self, rotate_angle=0, forward=0):
        if rotate_angle != 0:
            self.vehicle.rotate(rotate_angle)
        if forward != 0:
            self.vehicle.slide(Point(0, forward, 0))

        # if self.use_stabilize:
        #     time.sleep(1)
        #     ret, frame = self.cap.read()
        #     self.init_target(frame)

    def do_command(self, command, value=None):
        if command == 'init_tracking':
            # set target box and init tracker
            target = None
            if self.selected_object is not None:
                target = self.trackers[self.selected_object]
            else:
                if self.use_stabilize:
                    target = self.stabilize_box
                else:
                    target = self.center_box

            self.do_command('start_tracking', target.get_target())

        if command == 'start_tracking':
            self.need_tracking = True
            self.target = value
        if command == 'stop_tracking':
            self.need_tracking = False
            self.target = None
            self.tracker = None
        if command == 'next_target':
            if self.selected_object is not None:
                self.selected_object += 1
                if self.selected_object >= len(self.trackers):
                    self.selected_object = 0
        if command == 'prev_target':
            if self.selected_object is not None:
                self.selected_object -= 1
                if self.selected_object < 0:
                    self.selected_object = len(self.trackers) - 1

    def run(self):
        if os.name == 'nt':
            self.cap = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)  # Initialize camera capture in  Windows
            # self.cap = cv.VideoCapture(self.camera_id)  # Initialize camera capture in Linux
        else:
            self.cap = cv.VideoCapture(self.camera_id)  # Initialize camera capture in Linux

        # f_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        # f_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        f_width = FRAME_WIDTH
        f_height = FRAME_HEIGHT
        self.strategy.set_screen_size(f_width, f_height)  # set screen size
        sy = int(f_height / 2)  # calc screen center
        sx = int(f_width / 2)

        # define the target box size
        b_size = self.stabilize_size
        box = list((sx - b_size, sy - b_size, b_size * 2, b_size * 2))
        red = (0, 0, 255)
        self.stabilize_box = TargetObject(tuple(box), red)

        b_size = self.target_size
        box = list((sx - b_size, sy - b_size, b_size * 2, b_size * 2))
        self.center_box = TargetObject(tuple(box), red, True)

        # set fullscreen mode
        if self.fullscreen_mode:
            cv.namedWindow("Frame", cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty("Frame", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        last_update = 0
        last_model_update = 0
        lost_target = None  # last track result
        selected_color = (0, 0, 255)  # red
        object_detection = None
        if self.use_object_detection:
            object_detection = ObjectDetection()

        while True:
            ret, frame = self.cap.read()
            if int(frame.shape[1]) != f_width:  # frame `width`
                frame = cv.resize(frame, (f_width,f_height))


            if not ret:
             break

            now = time.time()

            # Tracking detetected objects
            if (self.use_object_detection) and (self.target is None):
                if (now - last_update) > 0.1:
                    last_update = now
                    for index, tracker in enumerate(self.trackers):
                        if tracker.update(frame):
                            if self.selected_object == index:
                                tracker.show(cv, frame, selected_color)
                            else:
                                tracker.show(cv, frame)
                        else:  # remove a lost object
                            if self.selected_object == index:
                                self.selected_object = None
                            self.trackers.remove(tracker)
            # Update model
            if (now - last_model_update) > 1:  # check Maivlink mode and Object Models each 1 second
                last_model_update = now
                if self.vehicle.able_trackig():  # waiting  for "Guided" mode
                    if self.use_object_detection:
                        self.vehicle.listen_command(self.do_command)
                    else:
                        self.do_command('init_tracking')
                else:
                    if self.target is not None:
                        self.do_command('stop_tracking')
                        lost_target = None

                if self.target is None:
                    if object_detection:
                        self.trackers = object_detection.update(frame, self.trackers)
                        # update selected_object
                        if self.selected_object is None:
                            if len(self.trackers) > 0:
                                self.selected_object = 0

            if self.need_tracking:
                if not lost_target:
                    if self.tracker is None:
                        self.init_tracker(frame)
                        self.strategy.update_target_pos(sx, sy)

                    if self.target is not None:
                        lost_target = not self.update_stratagy(frame)
                        if lost_target:
                            self.target = None

            key = cv.waitKey(1) & 0xFF
            if key == ord('t'):
                self.vehicle.arm_and_takeoff(5)
            if key == ord('r'):
                self.move_vehicle(10)
            if key == ord('l'):
                self.move_vehicle(-10)
            if key == ord('f'):
                self.move_vehicle(0, 10)
            if key == ord('b'):
                self.move_vehicle(0, -10)
            if key == ord('+'):
                self.do_command('next_target')
            if key == ord('-'):
                self.do_command('prev_target')
            if key == ord('*'):
                self.do_command('init_tracking')
            if key == ord(' '):
                self.do_command('stop_tracking')


            # show the target boxes
            if self.use_stabilize:
                self.stabilize_box.show(cv, frame)

            if self.center_box:
                self.center_box.show(cv, frame)

            if lost_target:
                cv.putText(frame, 'Lost target', (20, 20), cv.FONT_HERSHEY_SIMPLEX,
                           1, red, 1, cv.LINE_AA)

            cv.imshow("Frame", frame)

        self.cap.release()
        cv.destroyAllWindows()

    def update_stratagy(self, frame):
        success, new_box = self.track(frame)  # Track object

        # move drone if object found
        if success:
            #  mavik update position
            self.strategy.update_current_pos(new_box)

            ## the main function
            self.strategy.update_vehicle()

        return success

    def track(self, frame):
        if self.tracker.update(frame):
            self.tracker.show(cv, frame)
            return True, self.tracker.get_target()
        else:
            return False, None
