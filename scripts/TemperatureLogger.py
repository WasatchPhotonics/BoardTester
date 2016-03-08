""" rough and ready script to collect temperatures from a wasatch
photonics stroker protocol series device. Also uses the ThorLabsMeter
cross platform wrapper from FastPM100 to collect power readings.

Output:
    Create/Append to filename (default: combined_log.csv)
    timestamp: min,max,avg CCD Temp  min,max,avg Laser Temp,
               min,max,avg PM100 Reading, min,max,avg yellow thermistor,
               min,max,avg blue thermistor, min,max,avg amps



Example configuration:

    Start the Thorlabs Optical power meter software
    Set wavelength to 785, set high gain, no averaging

    cd BoardTester
    python setup.py develop
    python scripts/TemperatureLogger.py 

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

slapchop = devices.SlapChopDevice()

device = stroker_protocol.StrokerProtocolDevice()
result = device.connect()
serial = device.get_serial_number()

laser_enable_wait = 1
log.info("Turn laser on, wait %s seconds", laser_enable_wait)
device.set_laser_enable(1)
time.sleep(laser_enable_wait)

filename = "combined_log.csv"
log.info("Starting log of: %s to %s", serial, filename)

period = 1
samples = 100
sleep_interval = (float(period) / float(samples))
log.info("Logging %s samples every %s seconds (sample rate: %s)", \
         samples, period, sleep_interval)
            

l_temps = []
c_temps = []
l_power = []

y_therm = []
b_therm = []
e_amper = []

def write_data():

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

        # Electrical amperes group
        amp_str = ""
        for item in e_amper_grp:
            out_file.write("%s," % item)
        amp_str += "%2.2f," % item


        out_file.write("\n")

        log.info("%s %s %s %s %s %s", 
                 ccd_str, las_str, pow_str,
                 yel_str, blu_str, amp_str)

def get_data():
    l_temps.append(device.get_laser_temperature())
    c_temps.append(device.get_ccd_temperature())
    l_power.append(pm100usb.read())

    parts = slapchop.read()

    y_therm.append(parts[0])
    b_therm.append(parts[1])
    e_amper.append(parts[2])

def zmq_get_data():
    """ Like get data above, but also spew out on a zmq publisher
    socket.
    """
    l_temps.append(device.get_laser_temperature())
    c_temps.append(device.get_ccd_temperature())
    l_power.append(pm100usb.read())

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


while not stop_log:
    # Sample every sleep interval, write at every period
    time.sleep(sleep_interval)
    now_time = time.time()

    curr_time = abs(now_time - start_time)

    if curr_time >= period:
        write_data()

        l_temps = []
        c_temps = []
        l_power = []
        start_time = time.time()


    else:
        log.debug("Get data")
        #get_data()
        zmq_get_data()


#device.set_laser_enable(0)
