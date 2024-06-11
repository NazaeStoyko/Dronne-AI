

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
import time
import math
NEXT_PREV = 3 # channel 3
START_STOP = 4 # channel 4
SHIFT = 100

class MavikMessage(object):
    def __init__(self, channel,  neutral_value=1500):
        self.channel = channel
        self.confirm_message = True
        self.neutral_value = neutral_value

    def estimate_value(self, message):
        value = message[self.channel]
        if (value > (self.neutral_value-SHIFT)) and (value < (self.neutral_value+SHIFT)):
            if not self.confirm_message:
                self.confirm_message = True
                print("confirm_message = True")
        else:
            if value > (self.neutral_value+SHIFT):
                print(" msg 1: ", message)
                if self.confirm_message:
                    self.confirm_message = False
                    return 1

            if value < (self.neutral_value-SHIFT):
                print(" msg 2: ", message)
                if self.confirm_message:
                    self.confirm_message = False
                    return 2
        return 0



class MavikObject(object):
    # constructor function
    def __init__(self, connection_string, config={}):
        # connect to vehicle with dronekit
        # self.vehicle = self.get_vehicle_with_dronekit()
        self.connected=True
        self.sitl = None
        self.vehicle = None
        self.callback = None
        try:
            # Start SITL if no connection string specified
            if not connection_string:
                import dronekit_sitl
                self.sitl = dronekit_sitl.start_default()
                connection_string = self.sitl.connection_string()

            self.vehicle = connect(connection_string, wait_ready=True, baud=57600)
        except Exception as X:
            self.connected=False

    def isConnected(self):
        return self.connected

    def getAttitude(self):
        return self.vehicle.location.global_relative_frame.alt

    def able_trackig(self):
        return self.vehicle.mode.name == 'GUIDED'

    def rotate(self, angle):
        dir = 1
        if (angle < 0):
            dir = -1
        print(" angle -  %s" % (angle))
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,  # target system, target component
            115, #mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
            0,  # confirmation
            abs(angle),  # param 1, yaw in degrees
            0,  # param 2, yaw speed deg/s
            dir,  # param 3, direction -1 ccw, 1 cw
            1,  # param 4, relative offset 1, absolute angle 0
            0, 0, 0)  # param 5 ~ 7 not used
        # send command to vehicle
        # vehicle.send_mavlink(msg)
        # send command to vehicle

        self.vehicle.send_mavlink(msg)

    def slide(self, point, duration=2):
        speed_type = 0  # air speed
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            9, # mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
            2503,  # 0b100111000111, # type_mask (only speeds enabled), x:LSB & yaw_rate: MSB
            0,0, 0,  # x, y, z positions
            point.x, point.y, 0,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        )

        self.vehicle.send_mavlink(msg)
        print('mavik point - x', point.x, ', y ', point.y, ', z ', point.z)

    def velocity(self, point, duration=2):
        speed_type = 0  # air speed
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            8,
            4039,
            # mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            # 0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            point.x, point.y, point.z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        )

        # send command to vehicle
        # vehicle.send_mavlink(msg)
        # send command to vehicle
        now = time.time()
        first_update = now
        last_update = now
        step = 2

        self.vehicle.send_mavlink(msg)
        print('mavik point - x', point.x, ', y ', point.y, ', z ', point.z)

        # exit immediately if it's been too soon since the last update
        # while (now - first_update) < duration:
        #     now = time.time()
        #     if (now - last_update) > step:
        #         # for x in range(0, duration):
        #         self.conection.send_mavlink(msg)
        #         last_update = now
        #         # time.sleep(2)

    # Callback to update target
    def listen_callback(self,base, attr_name, msg):
        if not self.able_trackig():
            return
        if self.msg_next.estimate_value(msg) == 1:
            self.callback('next_target')
        if self.msg_next.estimate_value(msg) == 2:
            self.callback('prev_target')

        if self.msg_start.estimate_value(msg) == 1:
            self.callback('init_tracking')
        if self.msg_start.estimate_value(msg) == 2:
            self.callback('stop_tracking')

    def listen_command(self, callback):
        # Add observer for the vehicle's current location
        self.msg_next = MavikMessage(NEXT_PREV , 1000)
        self.msg_start = MavikMessage(START_STOP)
        self.callback = callback
        self.vehicle.add_attribute_listener('channels', self.listen_callback)

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in STABILIZE  mode
        self.vehicle.mode = VehicleMode("STABILIZE")
        time.sleep(2)

        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(2)


        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto
        #  (otherwise the command after Vehicle.simple_takeoff will execute
        #   immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)
