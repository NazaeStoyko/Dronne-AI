import time
import math
from BaseObject import Point
from Tracking.Helper import get_center


class ObjectStrategy(object):
    def __init__(self, vehicle, config):
        #rotate_mode = True, use_stabilize = False, velocity = 3, vel_update_rate = 1,  camera_in_front = True
        self.__vehicle = vehicle

        self.__targetPos = Point()
        self.__currentPos = Point()

        # timer to intermittently update
        self.last_update = time.time()

        self.rotate_mode = config.get('rotate_mode', True)
        # enable stabilize mode
        self.stabilize_activate(config.get('use_stabilize',False))

        # camera postion
        self.camera_in_front = config.get('camera',True)['in_front']

        # set default parameters
        self.vel_update_rate = config.get('vel_update_rate',1)  # update time  range in seconds
        self.velocity = config.get('vehicle',3)['velocity']  # default velocity 3 m/s
        self.set_screen_size(640, 480)  # default
        self.set_camera_AOV(config.get('camera',66)['h_angle'], config.get('camera',41)['v_angle'])  # camera's AOV

    def stabilize_activate(self, value):
        self.__stabilize = value

    def update_target_pos(self, x,y):
        self.__targetPos.update(x, y)

    def update_current_pos(self, box):
        (x, y) = get_center(box)
        self.__currentPos.update(x, y)

    def set_screen_size(self, w, h):
        self.screen_w = w
        self.screen_h = h

    def set_camera_AOV(self, x, y):
        self.camera_x_angle = x
        self.camera_y_angle = y

    def move_vehicle(self):
        shift = self.get_shift()
        # exclude small ajustments
        # if abs(shift.y) < 0.02:
        #     shift.y = 0
        self.send_mav_msg(shift)

    def get_shift(self):
        shift = Point()
        if self.__stabilize:
            h = self.__vehicle.getAttitude()
            print('Stratagy shift attitude - ', h)
            dx = self.__currentPos.x - self.__targetPos.x
            print('Stratagy shift dx - ', dx)
            dy = self.__currentPos.y - self.__targetPos.y
            print('Stratagy shift dy - ', dy)
            mx = (2 * h) * math.tan(self.camera_x_angle / 2 / 180 * math.pi) / self.screen_w
            print('Stratagy shift mx - ', mx)
            my = (2 * h) * math.tan(self.camera_y_angle / 2 / 180 * math.pi) / self.screen_h
            print('Stratagy shift my - ', my)
            shift.y = dx * mx  # because "y" slide in horizontal layout
            shift.x = dy * my  # because "x" slide in vertical layout
        else:
            shift.x = self.velocity
            dx = self.__currentPos.x - self.__targetPos.x
            print('Stratagy shift dx - ', dx)
            dy = self.__currentPos.y - self.__targetPos.y
            # dz = self.currentPos.z - self.targetPos.z
            awx = dx * (self.camera_x_angle / self.screen_w)
            print('Stratagy shift awx - ', awx)

            awy = dy * (self.camera_y_angle / self.screen_h)
            print('Stratagy shift awy - ', awy)

            y = shift.x * math.tan(awx / 180 * math.pi)
            print('Stratagy shift y - ', y)

            z = shift.x * math.tan(awy / 180 * math.pi)
            print('Stratagy shift z - ', z)

            shift.y = y
            shift.z = z
        return shift

    def send_mav_msg(self, shift):
        if self.__stabilize:
            if self.camera_in_front:
                angle = math.atan(shift.x / shift.y) / math.pi * 180
                self.__vehicle.rotate(angle)
            else:
                self.__vehicle.slide(shift)
        else:
            if self.rotate_mode:
                angle = math.atan(shift.y / shift.x) / math.pi * 180
                self.__vehicle.rotate(angle)
            else:
                self.__vehicle.velocity(shift)

    def update_vehicle(self):
        now = time.time()
        if (now - self.last_update) > self.vel_update_rate:
            self.last_update = now
            print('last update - ', now)

            x = self.__currentPos.x
            y = self.__currentPos.y
            print('last update pos - ', x, ' ', y)

            ## the main function
            self.move_vehicle()
