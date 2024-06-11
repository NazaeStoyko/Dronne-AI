#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function


# Set up option parsing to get connection string
import argparse
from MavikObject import MavikObject
from ObjectTracking import ObjectTracking
import yaml

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# Print the values as a dictionary
print(config)


parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode ')
parser.add_argument('--connect',
                    help="Vehicle connection target string.")
parser.add_argument('--is_moving_mode',  action='store_true',
                    help="Vehicle target tracking, by default is rotate mode")
parser.add_argument('--use_stabilize',  action='store_true',
                    help="Use stabilize before targeting, by default is false")
parser.add_argument('--use_prediction',  action='store_true',
                    help="Use prediction in object tracking, by default is false")
parser.add_argument('--not_fullscreen',  action='store_true',
                    help="Set standard output screen , by default is fullscreen ")
parser.add_argument('--use_object_detection',  action='store_true',
                    help="Use object detection before tracking, by default target should be in the center ")
#--connect udpout:192.168.233.129:14551
args = parser.parse_args()
connection_string = args.connect
config['rotate_mode'] = not args.is_moving_mode
config['use_prediction'] = args.use_prediction
config['use_stabilize'] = args.use_stabilize
config['fullscreen'] = not args.not_fullscreen
config['use_object_detection'] = args.use_object_detection
config['camera_id'] = 0 # default camera
# config['camera_in_front'] = True

# rotate_mode = True, camera_id = 0, use_prediction = False, fullscreen = True, use_stabilize = False, camera_in_front = True, use_object_detection = False
#rotate_mode, 0, use_prediction, fullscreen, use_stabilize, camera_in_front, use_object_detection
vehicle = MavikObject(connection_string, config)
if vehicle.isConnected():
    ot = ObjectTracking(vehicle , config)
    ot.run()
