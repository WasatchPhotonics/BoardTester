""" Based on TemperatureLogger.py, with laser pulsing independent of
data acquisition

see TemperatureLogger.py for details
"""

import os
import sys
import time
import numpy
import logging
import datetime
import zmq
log = logging.getLogger()
log.setLevel(logging.INFO)

frmt_str = "%(asctime)-8s %(message)s"
frmt = logging.Formatter(frmt_str)
strm = logging.StreamHandler(sys.stdout)
strm.setFormatter(frmt)
log.addHandler(strm)


from wasatchusb import stroker_protocol
from fastpm100 import devices

pm100usb = devices.ThorlabsMeter()
try:
    result = pm100usb.read()
except Exception as exc:
    print "Problem setting up power meter: %s" % exc
    print "Continuing without power meter"
    pm100usb = None


# There is only one slapchop device, return zeros if it is unavailable.
slapchop = None
try:
    slapchop = devices.SlapChopDevice()
except Exception as exc:
    print "Problem setting up slapchop: %s" % exc


device = stroker_protocol.StrokerProtocolDevice(pid=0x0014)
result = device.connect()
serial = device.get_serial_number()

laser_enable_wait = 1
log.info("Turn laser on, wait %s seconds", laser_enable_wait)
device.set_laser_enable(1)
time.sleep(laser_enable_wait)
#log.critical("Not turning laser on!")

filename = "combined_log.csv"
log.info("Starting log of: %s to %s", serial, filename)

period = 10
samples = 1000
sleep_interval = (float(period) / float(samples))
log.info("Logging %s samples every %s seconds (sample rate: %s)", \
         samples, period, sleep_interval)


l_temps = []
c_temps = []
l_power = []

y_therm = []
b_therm = []
e_amper = []

def write_data(laser_status=None):

    l_temp_grp  = [min(l_temps), max(l_temps), numpy.average(l_temps)]
    c_temp_grp  = [min(c_temps), max(c_temps), numpy.average(c_temps)]
    l_power_grp = [min(l_power), max(l_power), numpy.average(l_power)]

    y_therm_grp = [min(y_therm), max(y_therm), numpy.average(y_therm)]
    b_therm_grp = [min(b_therm), max(b_therm), numpy.average(b_therm)]
    e_amper_grp = [min(e_amper), max(e_amper), numpy.average(e_amper)]

    combined_data = c_temp_grp, l_temp_grp, l_power_grp

    timestamp = datetime.datetime.now()
    with open(filename, "a") as out_file:
        out_file.write("%s," % timestamp)

        # CCD Temperature groups:
        ccd_str = ""
        for item in c_temp_grp:
            out_file.write("%s," % item)
        ccd_str += "%2.2f," % item

        # Laser Temperature groups:
        las_str = ""
        for item in l_temp_grp:
            out_file.write("%s," % item)
        las_str += "%2.2f," % item

        # Laser power groups:
        pow_str = ""
        for item in l_power_grp:
            out_file.write("%s," % item)
        pow_str += "%2.2f," % item

        # Yellow thermistor group
        yel_str = ""
        for item in y_therm_grp:
            out_file.write("%s," % item)
        yel_str += "%2.2f," % item

        # Blue thermistor group
        blu_str = ""
        for item in b_therm_grp:
            out_file.write("%s," % item)
        blu_str += "%2.2f," % item

        # Electrical amperes group, or the laser status for easier
        # processing csv
        amp_str = ""
        if laser_status == None:
            for item in e_amper_grp:
                out_file.write("%s," % item)
            amp_str += "%2.2f," % item
        else:
            out_file.write("%s," % laser_status)
            item = laser_status
            amp_str += "%s," % laser_status



        out_file.write("\n")

        log.info("%s %s %s %s %s %s",
                 ccd_str, las_str, pow_str,
                 yel_str, blu_str, amp_str)

def zmq_get_data():
    """ Like get data above, but also spew out on a zmq publisher
    socket.
    """
    l_temps.append(device.get_laser_temperature())
    c_temps.append(device.get_ccd_temperature())

    if pm100usb != None:
        l_power.append(pm100usb.read())
    else:
        l_power.append(0.0)

    parts = (0, 0, 0)
    if slapchop is not None:
        parts = slapchop.read()
    y_therm.append(parts[0])
    b_therm.append(parts[1])
    e_amper.append(parts[2])

    topic = "temperatures_and_power"
    str_mesg = ("%s %s,%s,%s,%s,%s,%s" \
                % (topic, c_temps[-1], l_temps[-1], l_power[-1], \
                          y_therm[-1], b_therm[-1], e_amper[-1]
                  )
               )
    socket.send(str_mesg)

context = zmq.Context()
socket = context.socket(zmq.PUB)
port = "6545"
log.info("Setup zmq publisher on port %s", port)
socket.bind("tcp://*:%s" % port)

file_header = "Timestamp,CCD Min,CCD Max,CCD Average," \
              + "Laser Temperature Min,Laser Temperature Max," \
              + "Laser Temperature Average," \
              + "Laser Power Min,Laser Power Max," \
              + "Laser Power Average,"\
              + "Yellow thermistor min,Yellow Thermistor Max,Yellow Thermistor Average," \
              + "Blue thermistor min,Blue Thermistor Max,Blue Thermistor Average," \
              + "Amps Min,Amps Max,Amps Average,"

#header_str = "CCD Min, Max, Avg  Las Min, Max, Avg  " \
#             + "Pow Min, Max, Avg"
header_str = "CCD Avg  Las Avg Yellow Therm, Blue Therm, Amps"
log.info(header_str)

# Print header if file does not exist
if not os.path.exists(filename):
    with open(filename, "a") as out_file:
     out_file.write("%s\n" % file_header)

stop_log = False

start_time = time.time()

# Turn laser on wait 200 ms
# record data, wait 200 ms
# turn laser off wait 600 ms

# Every 200ms, do one of 5 actions
actions = ["on", "record", "off", "off", "off"]
action_sleep = 0.200
action_count = 0
action_time = time.time()


# Every 500ms, do one of two actions
actions = ["on", "off"]
action_sleep = 0.500
action_count = 0
action_time = time.time()
laser_status = "1"

while not stop_log:
    # Sample every sleep interval, write at every period
    time.sleep(sleep_interval)
    now_time = time.time()

    curr_time = abs(now_time - start_time)

    last_action = abs(now_time - action_time)
    if last_action >= action_sleep:
        #log.info("Action: %s", actions[action_count])

        if actions[action_count] == "on":
            device.set_laser_enable(1)
            laser_status = "1"
        elif actions[action_count] == "off":
            device.set_laser_enable(0)
            laser_status = "0"
        elif actions[action_count] == "record":
            log.info("Record data")

        action_count += 1

        if action_count >= len(actions):
            action_count = 0

        action_time = now_time




    if curr_time >= period:
        write_data(laser_status=laser_status)

        l_temps = []
        c_temps = []
        l_power = []
        y_therm = []
        b_therm = []
        e_amper = []
        start_time = time.time()


    else:
        log.debug("Get data")
        zmq_get_data()


    
