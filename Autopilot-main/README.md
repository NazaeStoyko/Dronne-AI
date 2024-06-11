# Autopilot for FPV drones.
This application provide vehicle control by Mavlink protocol using Object tracking.

Tracking is activated when the vehicle on "GUIDED" mode.

### Recommend schema
Digital Camera -> Companion computer -> Analog audio stream -> Flight controller 

Tested Companion computer : Raspberry Pi 4 , 4GB

You will get much better experience with Orange pi 5.
In order to run it in orange you might need to open UART0:
```
sudo orangepi-config
```
```
System -> Hardware -> uart0-m2

```
Reboot.

Then you need to check whether change has been applied.
```
ls /dev/ttyS*
```
and
```
sudo gpio serial /dev/ttyS0
```
Hence, your connection string should be `"/dev/ttyS0"`

Please see [Orange Pi docs](https://drive.google.com/drive/folders/1Bre2q0bGgXQuQlYaYDMvwstpvtHLmcgX), section 3.18.5 for more information

In case you have troubles with connection try to install `pyserial` lib. If you have any errors with tracker - install `opencv-contrib-python`.


Demo with SITL
https://youtu.be/pW_swFzizJY

This example show connection Raspberry by Mavlink 
https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html

### Required packages:
- dronekit              2.9.2, for Python > 3.09 need to use the patched version
  https://github.com/dronekit/dronekit-python/issues/1210
- opencv-python 4.9.0.80
- opencv-contrib-python 4.9.0.80
- numpy                 1.26.4
- ultralytics		8.2.0
- pyyaml		6.0.1
- pyserial

### update 04.06.24
Added the configuration file config.yaml
Default values :
 - camera's horizontal angle of view  - 66° 
 - camera's vertical angle of view  - 41° 
 - drone velocity - 3 m/s


### update 11.05.24
Improve README.md and error tips

### update 02.05.24
Added object detection ability before start tracking
Choose the target and start tracking by GCS jostick 

### update 24.04.24
Added the stabilize mode for drone

### update 04.04.24
Added prediction ability for the object tracking

### update 26.03.24
Provide horizontal and vertical tracking.


Parameters :

  **- connect** ( path to mavlink device )
  
  example : --connect /dev/ttyS0:57600

	for UDP use udp:127.0.0.1:14550, for Serial /dev/ttyS0:57600
  
  **- is_moving_mode** (switch to moving mode , by default rotate body instead of moving )
  
  example : --is_moving_mode
  
  **- use_prediction** (use prediction in object tracking, by default is false )

  example : --use_prediction

  **- not_fullscreen** (Set standard output screen , by default is fullscreen )

  example : --not_fullscreen
